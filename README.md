
![Tool](https://github.com/user-attachments/assets/c2a1677a-b42b-46c1-aa4b-8ed65eb1484c)

# ASN-Hunter - Advanced ASN Reconnaissance Tool

A sophisticated Python-based ASN reconnaissance tool designed for bug bounty hunters, penetration testers, and security researchers.

## Features

- **Comprehensive ASN Discovery**: Searches both PeeringDB and BGPView APIs
- **Interactive Selection**: Multiple selection methods with user-friendly interface
- **BGP.HE.NET Scraping**: Extracts complete IPv4/IPv6 prefix information with anti-bot measures
- **Professional UI**: Matrix-themed terminal interface with colored output
- **Multiple Export Formats**: JSON and CSV export capabilities
- **Error Resilience**: Comprehensive error handling with fallback mechanisms
- **Rate Limiting**: Intelligent delays to avoid API restrictions

## Installation

1. Clone or download the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python3 asn-hunter.py "tesla"
python3 asn-hunter.py "cloudflare"
```

### Advanced Options
```bash
# Verbose output
python3 asn-hunter.py "amazon" -v

# Export to JSON
python3 asn-hunter.py "meta" -o results.json

# Export to CSV
python3 asn-hunter.py "google" -o report.csv --format csv

# Custom delay (for slower connections)
python3 asn-hunter.py "microsoft" --delay 2

# Disable colors
python3 asn-hunter.py "apple" --no-color
```

## Interactive Selection

The tool provides multiple ways to select ASNs:

- **Single/Multiple**: `1,3,5`
- **Ranges**: `1-5` 
- **All**: `all`
- **Quit**: `q`

## Output Features

- **IP Space Calculation**: Automatic calculation of total IPv4 address space
- **Organized Display**: Professional formatting with ASN details
- **Source Attribution**: Shows data sources for each result
- **Comprehensive Stats**: IPv4/IPv6 prefix counts and address space

## Data Sources

1. **PeeringDB API**: Organization and ASN information
2. **BGPView API**: ASN search and details
3. **BGP.HE.NET**: Complete IPv4/IPv6 prefix scraping
4. **WHOIS**: Fallback mechanism for prefix discovery

## Error Handling

- Connection failure recovery
- Rate limit detection and handling
- HTTP error management
- Fallback mechanisms for data collection
- User-friendly error messages

## Security Note

This tool is designed for legitimate security research, bug bounty hunting, and penetration testing. Use responsibly and in accordance with applicable laws and regulations.

## Examples

### Search for Tesla
```bash
python3 asn-hunter.py tesla
```

This will:
1. Search PeeringDB and BGPView for "tesla"
2. Present interactive selection of found ASNs
3. Scrape bgp.he.net for complete prefix information
4. Display professional reconnaissance report

### Export Results
```bash
python3 asn-hunter.py "cloudflare" -o cloudflare-asns.json
```

Creates a JSON file with:
- ASN information
- Complete IPv4/IPv6 prefix lists
- IP address space calculations
- Timestamp and metadata

## Troubleshooting

### Connection Issues
- Check internet connectivity
- Try increasing delay: `--delay 3`
- Use verbose mode: `-v`

### No Results Found
- Try broader search terms
- Check spelling variations
- Use alternative names (e.g., "meta" vs "facebook")

### Rate Limiting
- Tool automatically handles rate limits
- Increase delay between requests if needed
- BGP.HE.NET scraping includes built-in delays

## License

This tool is provided for educational and legitimate security research purposes only.
