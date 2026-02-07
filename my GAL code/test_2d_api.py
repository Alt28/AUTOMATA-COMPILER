import requests
import json

code = """root() {
 seed m[2][2] = {{1, 2}, {3, 4}};
 plant(m[1][1], m[2][2]);
 reclaim;
}"""

print("Testing 2D array code:")
print(code)
print("\n" + "="*60)

# Test with server API
url = "http://localhost:5000/api/parse"
payload = {"code": code}

try:
    response = requests.post(url, json=payload)
    result = response.json()
    
    print("\nPARSE RESULT:")
    print(json.dumps(result, indent=2))
    
    if result.get("success"):
        print("\n✓ Parse successful! 2D arrays are now supported!")
    else:
        print("\n✗ Parse failed:")
        for error in result.get("errors", []):
            print(f"  {error}")
            
except requests.exceptions.ConnectionError:
    print("\nERROR: Server is not running. Start it with: python .\\Backend\\server.py")
except Exception as e:
    print(f"\nERROR: {e}")
