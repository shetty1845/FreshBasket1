import os

def check_structure():
    print("Checking FreshBasket project structure...\n")
    
    # Check static folder
    if os.path.exists('static'):
        print("✓ static/ folder exists")
        if os.path.exists('static/style.css'):
            print("  ✓ static/style.css exists")
            print(f"     Size: {os.path.getsize('static/style.css')} bytes")
        else:
            print("  ✗ static/style.css NOT FOUND!")
            
        if os.path.exists('static/main.js'):
            print("  ✓ static/main.js exists")
        else:
            print("  ✗ static/main.js NOT FOUND!")
    else:
        print("✗ static/ folder NOT FOUND!")
        print("  → Create it: mkdir static")
    
    # Check templates folder
    if os.path.exists('templates'):
        print("\n✓ templates/ folder exists")
        templates = ['base.html', 'index.html', 'products.html', 'cart.html', 
                    'login.html', 'register.html', '404.html', '500.html']
        for template in templates:
            path = f'templates/{template}'
            if os.path.exists(path):
                print(f"  ✓ {template}")
            else:
                print(f"  ✗ {template} missing")
    else:
        print("\n✗ templates/ folder NOT FOUND!")
        print("  → Create it: mkdir templates")
    
    # Check app.py
    if os.path.exists('app.py'):
        print("\n✓ app.py exists")
    else:
        print("\n✗ app.py NOT FOUND!")

if __name__ == '__main__':
    check_structure()
