import os
import json
import glob

def find_client_secret_file():
    """
    Sucht nach der client_secret JSON-Datei in allen Unterordnern
    des aktuellen Verzeichnisses und dessen übergeordneten Verzeichnissen
    """
    # Aktuelles Verzeichnis und übergeordnete Verzeichnisse durchsuchen
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Suche in aktueller Datei-Directory und allen übergeordneten bis zur Wurzel
    search_dirs = []
    temp_dir = current_dir
    
    # Gehe nach oben bis zum Wurzelverzeichnis und sammle alle Pfade
    while True:
        search_dirs.append(temp_dir)
        parent_dir = os.path.dirname(temp_dir)
        if parent_dir == temp_dir:  # Wir sind bei der Wurzel angekommen
            break
        temp_dir = parent_dir
    
    # Durchsuche alle gesammelten Verzeichnisse
    for search_dir in search_dirs:
        # Suche nach client_secret*.json Dateien rekursiv in allen Unterordnern
        pattern = os.path.join(search_dir, "**", "client_secret*.json")
        matching_files = glob.glob(pattern, recursive=True)
        
        if matching_files:
            # Nimm die erste gefundene Datei
            return matching_files[0]
    
    # Fallback: Suche im gesamten Projekt-Verzeichnis (falls nichts gefunden wurde)
    project_root = os.path.dirname(current_dir)  # Eine Ebene höher als .dev
    pattern = os.path.join(project_root, "**", "client_secret*.json")
    matching_files = glob.glob(pattern, recursive=True)
    
    if matching_files:
        return matching_files[0]
    
    return None

def load_client_secret():
    """
    Lädt die client_secret JSON-Datei und gibt den Inhalt zurück
    """
    client_secret_path = find_client_secret_file()
    
    if not client_secret_path:
        raise FileNotFoundError("Keine client_secret JSON-Datei gefunden!")
    
    print(f"Client Secret Datei gefunden: {client_secret_path}")
    
    try:
        with open(client_secret_path, 'r', encoding='utf-8') as file:
            client_secret_data = json.load(file)
        return client_secret_data, client_secret_path
    except json.JSONDecodeError as e:
        raise ValueError(f"Fehler beim Parsen der JSON-Datei: {e}")
    except Exception as e:
        raise Exception(f"Fehler beim Laden der Datei: {e}")

def create_env_from_client_secret():
    """
    Erstellt eine .env Datei basierend auf den Client Secret Daten
    """
    try:
        client_data, file_path = load_client_secret()
        
        if 'web' in client_data:
            web_config = client_data['web']
            
            # Pfad zur .env Datei (im übergeordneten Verzeichnis)
            env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
            
            # .env Inhalt erstellen
            env_content = f"""# Google OAuth Konfiguration
GOOGLE_CLIENT_ID={web_config.get('client_id', '')}
GOOGLE_CLIENT_SECRET={web_config.get('client_secret', '')}
GOOGLE_PROJECT_ID={web_config.get('project_id', '')}

# Weitere Konfiguration
SECRET_KEY=your-secret-key-here
DEBUG=True
"""
            
            # .env Datei schreiben
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            
            print(f"✅ .env Datei erstellt: {env_path}")
            return env_path
            
    except Exception as e:
        print(f"❌ Fehler beim Erstellen der .env Datei: {e}")
        return None

# Beispiel für die Verwendung
if __name__ == "__main__":
    try:
        # Lade die Client Secret Daten
        client_data, file_path = load_client_secret()
        
        print(f"✅ Client Secret erfolgreich geladen von: {file_path}")
        print(f"📁 Dateiname: {os.path.basename(file_path)}")
        
        # Zeige verfügbare Keys (ohne sensible Daten anzuzeigen)
        if 'web' in client_data:
            print("🔑 Verfügbare Web-Client Konfiguration gefunden")
            web_config = client_data['web']
            print(f"   - Client ID: {web_config.get('client_id', 'N/A')[:20]}...")
            print(f"   - Project ID: {web_config.get('project_id', 'N/A')}")
            
            # Frage ob .env Datei erstellt werden soll
            create_env = input("\n📝 Möchtest du eine .env Datei erstellen? (y/n): ").lower().strip()
            if create_env == 'y':
                create_env_from_client_secret()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
