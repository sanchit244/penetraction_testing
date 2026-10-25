import ssl
import socket
import requests
from datetime import datetime
from typing import List
from models.schemas import VulnerabilitySchema, SeverityEnum
from urllib.parse import urlparse


class SSLScanner:
    """SSL/TLS configuration scanner"""

    WEAK_PROTOCOLS = ['SSLv2', 'SSLv3', 'TLSv1', 'TLSv1.1']
    WEAK_CIPHERS = [
        'NULL', 'EXPORT', 'DES', 'RC4', 'MD5',
        'PSK', 'SRP', 'CAMELLIA', 'SEED', 'IDEA', 'AECDH'
    ]

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for SSL/TLS vulnerabilities"""
        vulnerabilities = []

        try:
            parsed_url = urlparse(url)
            if parsed_url.scheme != 'https':
                vulnerabilities.append(
                    VulnerabilitySchema(
                        name="No HTTPS",
                        description="Website does not use HTTPS encryption",
                        severity=SeverityEnum.CRITICAL,
                        cvss_score=9.1,
                        url=url,
                        method="GET",
                        evidence=f"URL uses {parsed_url.scheme} protocol",
                        remediation="Enable HTTPS on the web server and redirect all HTTP traffic to HTTPS",
                        references=[
                            "https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/09-Testing_for_Weak_Cryptography/01-Testing_for_Weak_SSL_TLS_Ciphers"
                        ],
                        cwe_id="CWE-319"
                    )
                )
                return vulnerabilities

            hostname = parsed_url.hostname
            port = parsed_url.port or 443

            # Check certificate validity
            try:
                context = ssl.create_default_context()
                with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                    with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                        cert = ssock.getpeercert()

                        # Check certificate expiration
                        not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                        days_until_expiry = (not_after - datetime.now()).days

                        if days_until_expiry < 0:
                            vulnerabilities.append(
                                VulnerabilitySchema(
                                    name="Expired SSL Certificate",
                                    description="SSL certificate has expired",
                                    severity=SeverityEnum.CRITICAL,
                                    cvss_score=8.1,
                                    url=url,
                                    evidence=f"Certificate expired on {not_after}",
                                    remediation="Renew the SSL certificate immediately",
                                    references=["https://cwe.mitre.org/data/definitions/298.html"],
                                    cwe_id="CWE-298"
                                )
                            )
                        elif days_until_expiry < 30:
                            vulnerabilities.append(
                                VulnerabilitySchema(
                                    name="SSL Certificate Expiring Soon",
                                    description=f"SSL certificate expires in {days_until_expiry} days",
                                    severity=SeverityEnum.MEDIUM,
                                    cvss_score=5.3,
                                    url=url,
                                    evidence=f"Certificate expires on {not_after}",
                                    remediation="Renew the SSL certificate before expiration",
                                    references=["https://cwe.mitre.org/data/definitions/298.html"],
                                    cwe_id="CWE-298"
                                )
                            )

                        # Check TLS version
                        tls_version = ssock.version()
                        if tls_version in self.WEAK_PROTOCOLS:
                            vulnerabilities.append(
                                VulnerabilitySchema(
                                    name="Weak TLS Protocol",
                                    description=f"Server supports weak TLS protocol: {tls_version}",
                                    severity=SeverityEnum.HIGH,
                                    cvss_score=7.5,
                                    url=url,
                                    evidence=f"TLS version: {tls_version}",
                                    remediation="Disable support for TLS 1.0, TLS 1.1, and all SSL versions. Use TLS 1.2 or higher.",
                                    references=["https://cwe.mitre.org/data/definitions/327.html"],
                                    cwe_id="CWE-327"
                                )
                            )

            except ssl.SSLError as e:
                vulnerabilities.append(
                    VulnerabilitySchema(
                        name="SSL Configuration Error",
                        description=f"SSL/TLS configuration issue detected",
                        severity=SeverityEnum.HIGH,
                        cvss_score=7.4,
                        url=url,
                        evidence=str(e),
                        remediation="Review and fix SSL/TLS configuration",
                        references=["https://owasp.org/www-project-web-security-testing-guide/"],
                        cwe_id="CWE-295"
                    )
                )

        except Exception as e:
            print(f"Error scanning SSL/TLS: {e}")

        return vulnerabilities
