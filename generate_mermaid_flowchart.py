#!/usr/bin/env python3
"""Generate Mermaid flowchart for data architecture"""

mermaid_diagram = """
# BOZANKAYA SSH TAKIP SİSTEMİ - VERI AKIŞI ARKİTEKTÜRÜ

graph TD
    A["🔐 LOGGED IN USER<br/>current_project = 'belgrad'"] 
    
    %% Page Routes
    B["📊 ANA SAYFA<br/>/dashboard"]
    C["📋 SERVİS DURUMU<br/>/servis/durumu"]
    D["🔧 BAKIM SAYFASI<br/>/bakim"]
    E["⚠️ ARIZA SAYFASI<br/>/ariza"]
    
    %% Data Sources in PROJECT FOLDER
    F["📁 data/belgrad/<br/>Veriler.xlsx"]
    G["📁 data/belgrad/<br/>Belgrad-Bakım.xlsx"]
    H["📁 data/belgrad/<br/>BEL25_FRACAS.xlsx"]
    I["📁 data/belgrad/<br/>FR_010_R06_SSH HBR.xlsx"]
    
    %% Database Tables
    J["💾 Equipment Table<br/>(project_code='belgrad')"]
    K["💾 ServiceStatus Table<br/>(project_code='belgrad')"]
    L["💾 WorkOrder Table<br/>(project_code='belgrad')"]
    M["💾 Failure Table<br/>(project_code='belgrad')"]
    
    %% Calculations
    N["🧮 Stats Calculation<br/>aktif, servis_disi, isletme<br/>toplam, availability"]
    O["🧮 Equipment Hierarchy<br/>parent_id relationships"]
    P["🧮 Maintenance Plan<br/>MTTR, MTBF calculations"]
    
    %% Output
    Q["🎨 HTML Template<br/>servis_durumu_enhanced.html"]
    R["📊 JSON Response<br/>/servis/durumu/tablo"]
    S["📈 Chart/Graph<br/>Pie, Bar, Line"]
    T["📑 Data Table<br/>Equipment details"]
    
    %% User sees
    U["👁️ USER SEES<br/>- Stat Cards<br/>- Charts<br/>- Tables"]
    
    A -->|Login| B
    A -->|Navigate| C
    A -->|Navigate| D
    A -->|Navigate| E
    
    B -->|Fetch| F
    B -->|Query| J
    B -->|Query| K
    
    C -->|Read| F
    C -->|Query| J
    C -->|Query| K
    C -->|Calculate| N
    C -->|Render| Q
    
    D -->|Fetch| G
    D -->|Query| L
    D -->|Calculate| P
    
    E -->|Fetch| H
    E -->|Query| M
    
    J -->|Project Filter<br/>WHERE project_code| N
    K -->|Today Filter<br/>WHERE date=today| N
    
    F -->|Extract tram_id list<br/>Sayfa2| J
    
    Q -->|Display| U
    R -->|AJAX Update| Q
    N -->|Stats| R
    N -->|Stats| S
    K -->|Table Data| T
    T -->|HTML| U
    S -->|Chart HTML| U
    
    style A fill:#4CAF50,stroke:#2E7D32,color:#fff
    style B fill:#2196F3,stroke:#1565C0,color:#fff
    style C fill:#2196F3,stroke:#1565C0,color:#fff
    style D fill:#2196F3,stroke:#1565C0,color:#fff
    style E fill:#2196F3,stroke:#1565C0,color:#fff
    style F fill:#FF9800,stroke:#E65100,color:#fff
    style G fill:#FF9800,stroke:#E65100,color:#fff
    style H fill:#FF9800,stroke:#E65100,color:#fff
    style I fill:#FF9800,stroke:#E65100,color:#fff
    style J fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style K fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style L fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style M fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style N fill:#F44336,stroke:#C62828,color:#fff
    style O fill:#F44336,stroke:#C62828,color:#fff
    style P fill:#F44336,stroke:#C62828,color:#fff
    style Q fill:#00BCD4,stroke:#00838F,color:#fff
    style R fill:#00BCD4,stroke:#00838F,color:#fff
    style S fill:#8BC34A,stroke:#558B2F,color:#fff
    style T fill:#8BC34A,stroke:#558B2F,color:#fff
    style U fill:#FFD700,stroke:#FF6F00,color:#000
"""

diagram2 = """
# SERVIS DURUMU SAYFASI DETAYLI AKIŞ

graph LR
    A["🔐 USER<br/>belgrad proyesi"] 
    A1["Sayfaya Giriş<br/>/servis/durumu"]
    
    B1["📖 EXCEL OKU<br/>data/belgrad/<br/>Veriler.xlsx"]
    B2["Sayfa2, tram_id<br/>Sütunu"]
    B3["25 Tram ID<br/>1531-1555"]
    
    C1["🗄️ DB SORGULA<br/>Equipment<br/>.filter_by()"]
    C2["WHERE<br/>project_code=<br/>'belgrad'"]
    C3["25 Equipment<br/>Kayıt"]
    
    D1["📅 BUGÜNÜN VERİSİ<br/>ServiceStatus<br/>.filter_by()"]
    D2["WHERE<br/>date='2026-02-20'<br/>project_code=<br/>'belgrad'"]
    D3["25 Status Kayıt<br/>Servis/Arıza/İşletme"]
    
    E1["🧮 HESAPLA STATİSTİK"]
    E2["Durumları Analiz Et<br/>Status Values"]
    E3["Sabit: Total=25"]
    E4["Sayılarını Bul<br/>aktif, ariza, isletme"]
    E5["Yüzde Hesapla<br/>(aktif/25)*100"]
    
    E6["📊 SONUÇ<br/>stats dict"]
    E7["{operational:9<br/>outofservice:8<br/>maintenance:8<br/>total:25<br/>availability:36.0}"]
    
    F1["🎨 TEMPLATE RENDER<br/>servis_durumu_enhanced.html"]
    F2["Kartları Boş Göster<br/>(HTML yüklenir)"]
    F3["0 değerler ile"]
    
    G1["⚡ JAVASCRIPT<br/>refreshTable()"]
    G2["fetch('/servis/durumu/tablo')"]
    
    H1["🔗 API ENDPOINT<br/>/servis/durumu/tablo"]
    H2["Backend hesapla<br/>stats dict"]
    H3["JSON döner<br/>{stats, table_data}"]
    
    I1["📈 JAVASCRIPT GÜNCELLE<br/>document.getElementBy..."]
    I2["Kartları Doldur<br/>Gerçek Sayılarla"]
    I3["totalVehicles=25<br/>operationalCount=9<br/>outofserviceCount=8<br/>maintenanceCount=8<br/>avgAvailability=36.0%"]
    
    J1["👁️ FINAL RESULT<br/>User Görüyor"]
    J2["Başlıklar: 25 | 9 | 8 | 8 | 36.0%"]
    J3["Tablo: Equipment × Status"]
    J4["Grafikler: Pie/Bar/Line"]
    
    A -->|Sayfa Yükle| A1
    A1 -->|1. EXCEL OKU| B1
    B1 -->|Tab: Sayfa2| B2
    B2 -->|Extracted| B3
    
    A1 -->|2. DB SORGULA| C1
    C1 -->|Filter| C2
    C2 -->|25 Kayıt| C3
    
    A1 -->|3. DURUM VERİSİ| D1
    D1 -->|WHERE Clause| D2
    D2 -->|25 Kayıt| D3
    
    B3 -->|Referans| E1
    C3 -->|Equipment List| E1
    D3 -->|Status Values| E1
    
    E1 -->|Loop değerler| E2
    E2 -->|Tarayan| E3
    E3 -->|Bulunur| E4
    E4 -->|Matematiğle| E5
    E5 -->|Stats Dict| E6
    E6 -->|Sonuç| E7
    
    A1 -->|HTML Render| F1
    F1 -->|Jinja2| F2
    F2 -->|Initial| F3
    
    F3 -->|Sayfayükle| G1
    G1 -->|AJAX Query| G2
    G2 -->|GET Request| H1
    
    E7 -->|Backend'de| H2
    H2 -->|Tekrar Hesapla| H3
    
    H3 -->|Response| I1
    I1 -->|innerHTML=| I2
    I2 -->|Update Card Values| I3
    
    I3 -->|User Görür| J1
    J1 -->|Stat Cards| J2
    J1 -->|Table| J3
    J1 -->|Charts| J4
    
    style A fill:#4CAF50,stroke:#2E7D32,color:#fff
    style A1 fill:#4CAF50,stroke:#2E7D32,color:#fff
    style B1 fill:#FF9800,stroke:#E65100,color:#fff
    style B2 fill:#FF9800,stroke:#E65100,color:#fff
    style B3 fill:#FF9800,stroke:#E65100,color:#fff
    style C1 fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style C2 fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style C3 fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style D1 fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style D2 fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style D3 fill:#9C27B0,stroke:#6A1B9A,color:#fff
    style E1 fill:#F44336,stroke:#C62828,color:#fff
    style E2 fill:#F44336,stroke:#C62828,color:#fff
    style E3 fill:#F44336,stroke:#C62828,color:#fff
    style E4 fill:#F44336,stroke:#C62828,color:#fff
    style E5 fill:#F44336,stroke:#C62828,color:#fff
    style E6 fill:#F44336,stroke:#C62828,color:#fff
    style E7 fill:#F44336,stroke:#C62828,color:#fff
    style F1 fill:#00BCD4,stroke:#00838F,color:#fff
    style F2 fill:#00BCD4,stroke:#00838F,color:#fff
    style F3 fill:#00BCD4,stroke:#00838F,color:#fff
    style G1 fill:#00BCD4,stroke:#00838F,color:#fff
    style G2 fill:#00BCD4,stroke:#00838F,color:#fff
    style H1 fill:#E91E63,stroke:#880E4F,color:#fff
    style H2 fill:#E91E63,stroke:#880E4F,color:#fff
    style H3 fill:#E91E63,stroke:#880E4F,color:#fff
    style I1 fill:#00BCD4,stroke:#00838F,color:#fff
    style I2 fill:#00BCD4,stroke:#00838F,color:#fff
    style I3 fill:#00BCD4,stroke:#00838F,color:#fff
    style J1 fill:#FFD700,stroke:#FF6F00,color:#000
    style J2 fill:#FFD700,stroke:#FF6F00,color:#000
    style J3 fill:#FFD700,stroke:#FF6F00,color:#000
    style J4 fill:#FFD700,stroke:#FF6F00,color:#000
"""

print("Mermaid Diagram 1:")
print(mermaid_diagram)
print("\n\n" + "="*80 + "\n\n")
print("Mermaid Diagram 2:")
print(diagram2)
