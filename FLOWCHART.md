# CMMS Sistem Flowchart

## 1. Genel Sistem Mimarisi

```mermaid
graph TB
    User[Kullanıcı] --> Login[Login Sayfası]
    Login --> Auth{Kimlik Doğrulama}
    Auth -->|Başarılı| Dashboard[Dashboard]
    Auth -->|Başarısız| Login
    
    Dashboard --> Equipment[Ekipman Yönetimi]
    Dashboard --> WorkOrder[İş Emri Yönetimi]
    Dashboard --> Maintenance[Bakım Planları]
    Dashboard --> KPI[KPI & Raporlama]
    Dashboard --> Users[Kullanıcı Yönetimi]
    
    Equipment --> EquipDetail[Ekipman Detay]
    Equipment --> SensorData[Sensör Verileri]
    
    WorkOrder --> WODetail[İş Emri Detay]
    WorkOrder --> MainLog[Bakım Kayıtları]
    
    Maintenance --> Plans[Bakım Planları]
    Maintenance --> Schedule[Planlama]
    
    KPI --> Analytics[Analiz & Metrikler]
    KPI --> Reports[Raporlar]
```

## 2. Kullanıcı Akış Şeması

```mermaid
flowchart TD
    Start([Sistem Başlangıç]) --> CheckAuth{Kimlik<br/>Doğrulandı mı?}
    
    CheckAuth -->|Hayır| LoginPage[Login Sayfası]
    LoginPage --> EnterCred[Kullanıcı Adı & Şifre Gir]
    EnterCred --> ValidateAuth{Geçerli mi?}
    
    ValidateAuth -->|Hayır| ErrorMsg[Hata Mesajı]
    ErrorMsg --> LoginPage
    
    ValidateAuth -->|Evet| UpdateLogin[Son Giriş Güncelle]
    UpdateLogin --> CheckAuth
    
    CheckAuth -->|Evet| CheckRole{Kullanıcı Rolü?}
    
    CheckRole -->|Admin| AdminDash[Admin Dashboard]
    CheckRole -->|Manager| ManagerDash[Manager Dashboard]
    CheckRole -->|Technician| TechDash[Teknisyen Dashboard]
    CheckRole -->|Operator| OpDash[Operatör Dashboard]
    
    AdminDash --> FullAccess[Tüm Modüller]
    ManagerDash --> LimitedAccess[Yönetim Modülleri]
    TechDash --> WorkAccess[İş & Bakım Modülleri]
    OpDash --> ViewAccess[Görüntüleme]
    
    FullAccess --> MainMenu[Ana Menü]
    LimitedAccess --> MainMenu
    WorkAccess --> MainMenu
    ViewAccess --> MainMenu
    
    MainMenu --> Logout[Çıkış Yap]
    Logout --> Start
```

## 3. Ekipman Yönetimi İş Akışı

```mermaid
flowchart TD
    EquipStart([Ekipman Modülü]) --> EquipList[Ekipman Listesi]
    
    EquipList --> Action{Aksiyon Seç}
    
    Action -->|Görüntüle| ViewEquip[Ekipman Detay]
    Action -->|Yeni Ekle| AddEquip[Yeni Ekipman Formu]
    Action -->|Düzenle| EditEquip[Ekipman Düzenle]
    Action -->|Filtrele| FilterEquip[Filtreleme]
    
    AddEquip --> ValidateEquip{Form Geçerli mi?}
    ValidateEquip -->|Hayır| FormError[Hata Göster]
    FormError --> AddEquip
    ValidateEquip -->|Evet| SaveEquip[Veritabanına Kaydet]
    SaveEquip --> EquipList
    
    ViewEquip --> ShowDetails[Detayları Göster]
    ShowDetails --> SensorGraph[Sensör Grafikleri]
    ShowDetails --> EquipHierarchy[Hiyerarşi Göster]
    ShowDetails --> RelatedWO[İlgili İş Emirleri]
    ShowDetails --> MainHistory[Bakım Geçmişi]
    
    EditEquip --> UpdateDB[Güncelle]
    UpdateDB --> EquipList
    
    FilterEquip --> FilterResults[Filtrelenmiş Sonuçlar]
    FilterResults --> EquipList
```

## 4. İş Emri İş Akışı

```mermaid
flowchart TD
    WOStart([İş Emri Modülü]) --> WOList[İş Emri Listesi]
    
    WOList --> WOAction{Aksiyon}
    
    WOAction -->|Yeni Oluştur| CreateWO[Yeni İş Emri]
    WOAction -->|Detay| WODetail[İş Emri Detay]
    WOAction -->|Filtre| FilterWO[Durum/Öncelik Filtre]
    
    CreateWO --> SelectEquip[Ekipman Seç]
    SelectEquip --> WOForm[Form Doldur]
    WOForm --> AssignTech{Teknisyen<br/>Ata?}
    
    AssignTech -->|Evet| SelectTech[Teknisyen Seç]
    AssignTech -->|Hayır| SetPending[Pending Olarak Kaydet]
    SelectTech --> SetScheduled[Scheduled Olarak Kaydet]
    
    SetPending --> GenerateWO[İş Emri No Oluştur]
    SetScheduled --> GenerateWO
    GenerateWO --> SaveWO[Veritabanına Kaydet]
    SaveWO --> Notify[Bildirim Gönder]
    Notify --> WOList
    
    WODetail --> ShowWO[İş Emri Bilgileri]
    ShowWO --> WOStatus{Durum}
    
    WOStatus -->|Pending| CanSchedule[Planlanabilir]
    WOStatus -->|Scheduled| CanStart[Başlatılabilir]
    WOStatus -->|In Progress| CanComplete[Tamamlanabilir]
    WOStatus -->|Completed| Closed[Kapalı]
    
    CanStart --> UpdateStatus[Durumu Güncelle]
    CanComplete --> AddNotes[Tamamlama Notları]
    AddNotes --> AddCost[Gerçek Maliyet]
    AddCost --> UpdateStatus
    
    UpdateStatus --> AddMainLog[Bakım Kaydı Ekle]
    AddMainLog --> WODetail
```

## 5. Bakım Planlama İş Akışı

```mermaid
flowchart TD
    MainStart([Bakım Modülü]) --> MainMenu{Menü}
    
    MainMenu -->|Planlar| PlanList[Bakım Planları]
    MainMenu -->|Kayıtlar| LogList[Bakım Kayıtları]
    
    PlanList --> PlanAction{Aksiyon}
    
    PlanAction -->|Yeni Plan| CreatePlan[Yeni Plan Oluştur]
    PlanAction -->|Detay| PlanDetail[Plan Detayı]
    PlanAction -->|Düzenle| EditPlan[Plan Düzenle]
    
    CreatePlan --> SelectEquipPlan[Ekipman Seç]
    SelectEquipPlan --> SetType{Plan Tipi}
    
    SetType -->|Preventive| SetInterval[Periyot Belirle]
    SetType -->|Predictive| SetCondition[Koşul Belirle]
    
    SetInterval --> SchedulePlan[Planlama Tarihi]
    SetCondition --> SetThreshold[Eşik Değerler]
    SetThreshold --> SchedulePlan
    
    SchedulePlan --> SavePlan[Planı Kaydet]
    SavePlan --> AutoWO{Otomatik İş<br/>Emri Oluştur?}
    
    AutoWO -->|Evet| CreateAutoWO[İş Emri Oluştur]
    AutoWO -->|Hayır| PlanList
    CreateAutoWO --> PlanList
    
    PlanDetail --> ShowPlanInfo[Plan Bilgileri]
    ShowPlanInfo --> RelatedLogs[İlgili Kayıtlar]
    ShowPlanInfo --> NextSchedule[Sonraki Tarih]
    
    LogList --> AddLog[Yeni Kayıt Ekle]
    AddLog --> LinkWO[İş Emri Bağla]
    LinkWO --> LogDetails[Kayıt Detayları]
    LogDetails --> SaveLog[Kayıt Kaydet]
    SaveLog --> UpdateKPI[KPI Güncelle]
    UpdateKPI --> LogList
```

## 6. KPI & Analiz İş Akışı

```mermaid
flowchart TD
    KPIStart([KPI Modülü]) --> KPIDash[KPI Dashboard]
    
    KPIDash --> ShowMetrics[Metrikleri Göster]
    ShowMetrics --> MTBF[MTBF - Arıza Arası Süre]
    ShowMetrics --> MTTR[MTTR - Onarım Süresi]
    ShowMetrics --> Availability[Kullanılabilirlik]
    ShowMetrics --> Reliability[Güvenilirlik]
    ShowMetrics --> OEE[OEE - Ekipman Etkinliği]
    
    KPIDash --> CalcAction{Hesaplama}
    
    CalcAction -->|Manuel| ManualCalc[Manuel KPI Hesapla]
    CalcAction -->|Otomatik| AutoCalc[Otomatik Hesaplama]
    
    ManualCalc --> SelectPeriod[Dönem Seç]
    SelectPeriod --> CollectData[Veri Topla]
    
    CollectData --> GetFailures[Arıza Verileri]
    CollectData --> GetMaintenance[Bakım Verileri]
    CollectData --> GetSensor[Sensör Verileri]
    
    GetFailures --> Calculate[KPI Hesapla]
    GetMaintenance --> Calculate
    GetSensor --> Calculate
    
    Calculate --> CompareStandards{Standartlar<br/>ile Karşılaştır}
    
    CompareStandards -->|ISO 55000| ISO55000Check[Asset Management]
    CompareStandards -->|EN 15341| EN15341Check[Maintenance KPI]
    
    ISO55000Check --> GenerateReport[Rapor Oluştur]
    EN15341Check --> GenerateReport
    
    GenerateReport --> SaveKPI[KPI Kaydet]
    SaveKPI --> Visualize[Grafikleri Göster]
    Visualize --> Export{Dışa Aktar?}
    
    Export -->|PDF| ExportPDF[PDF Oluştur]
    Export -->|Excel| ExportExcel[Excel Oluştur]
    Export -->|Hayır| KPIDash
    
    ExportPDF --> Download[İndir]
    ExportExcel --> Download
    Download --> KPIDash
```

## 7. Veri Akışı Diyagramı

```mermaid
flowchart LR
    subgraph Input [Veri Girişi]
        Sensor[Sensör Verileri]
        Manual[Manuel Girişler]
        Schedule[Planlama]
    end
    
    subgraph Processing [İşleme Katmanı]
        Validation[Doğrulama]
        Business[İş Mantığı]
        Calculation[Hesaplama]
    end
    
    subgraph Storage [Depolama]
        Database[(SQLite Database)]
        Logs[Log Dosyaları]
    end
    
    subgraph Output [Çıktı]
        Dashboard[Dashboard]
        Reports[Raporlar]
        Alerts[Uyarılar]
        API[REST API]
    end
    
    Sensor --> Validation
    Manual --> Validation
    Schedule --> Validation
    
    Validation --> Business
    Business --> Calculation
    Calculation --> Database
    
    Business --> Logs
    
    Database --> Dashboard
    Database --> Reports
    Database --> API
    
    Calculation --> Alerts
    
    API --> External[Harici Sistemler]
```

## 8. Database İlişki Şeması

```mermaid
erDiagram
    USER ||--o{ WORKORDER : creates
    USER ||--o{ WORKORDER : assigned
    USER ||--o{ MAINTENANCELOG : performs
    
    EQUIPMENT ||--o{ EQUIPMENT : "parent-child"
    EQUIPMENT ||--o{ WORKORDER : has
    EQUIPMENT ||--o{ MAINTENANCEPLAN : has
    EQUIPMENT ||--o{ SENSORDATA : generates
    EQUIPMENT ||--o{ FAILURE : experiences
    
    WORKORDER ||--o{ MAINTENANCELOG : includes
    MAINTENANCEPLAN ||--o{ WORKORDER : generates
    
    EQUIPMENT ||--o{ INVENTORY : uses
    
    USER {
        int id PK
        string username
        string password_hash
        string email
        string role
        boolean is_active
    }
    
    EQUIPMENT {
        int id PK
        string equipment_code
        string name
        string equipment_type
        string status
        int parent_id FK
    }
    
    WORKORDER {
        int id PK
        string work_order_number
        int equipment_id FK
        int created_by FK
        int assigned_to FK
        string status
        string priority
    }
    
    MAINTENANCEPLAN {
        int id PK
        int equipment_id FK
        string plan_type
        int interval_days
        datetime next_due_date
    }
    
    MAINTENANCELOG {
        int id PK
        int work_order_id FK
        int technician_id FK
        datetime log_date
        text action_taken
    }
    
    SENSORDATA {
        int id PK
        int equipment_id FK
        string sensor_type
        float value
        datetime timestamp
    }
    
    FAILURE {
        int id PK
        int equipment_id FK
        datetime failure_date
        datetime resolution_date
        text description
    }
    
    KPI {
        int id PK
        date calculation_date
        float mtbf
        float mttr
        float availability
    }
    
    INVENTORY {
        int id PK
        int equipment_id FK
        string part_name
        int quantity
    }
```

## 9. Güvenlik & Yetkilendirme Akışı

```mermaid
flowchart TD
    Request[HTTP İstek] --> CheckSession{Session<br/>Var mı?}
    
    CheckSession -->|Hayır| Redirect401[401 Unauthorized]
    Redirect401 --> LoginRedirect[Login'e Yönlendir]
    
    CheckSession -->|Evet| LoadUser[Kullanıcı Yükle]
    LoadUser --> CheckActive{Aktif mi?}
    
    CheckActive -->|Hayır| Deactivated[Hesap Devre Dışı]
    Deactivated --> LoginRedirect
    
    CheckActive -->|Evet| CheckRole{Rol Kontrolü}
    
    CheckRole -->|Admin| FullPermission[Tüm Yetkiler]
    CheckRole -->|Manager| ManagerPermission[Yönetim Yetkileri]
    CheckRole -->|Technician| TechPermission[Teknisyen Yetkileri]
    CheckRole -->|Operator| OperatorPermission[Operatör Yetkileri]
    
    FullPermission --> ProcessRequest[İsteği İşle]
    ManagerPermission --> CheckResource{Kaynak<br/>Erişimi?}
    TechPermission --> CheckResource
    OperatorPermission --> CheckResource
    
    CheckResource -->|İzinli| ProcessRequest
    CheckResource -->|İzinsiz| Forbidden403[403 Forbidden]
    
    ProcessRequest --> LogAction[Aksiyonu Logla]
    LogAction --> Response[Yanıt Döndür]
    
    Forbidden403 --> ErrorPage[Hata Sayfası]
    ErrorPage --> Response
```

## 10. API Endpoint Akışı

```mermaid
flowchart LR
    subgraph API [REST API Endpoints]
        Auth[/api/auth]
        Equip[/api/equipment]
        WO[/api/workorders]
        Sensor[/api/sensors]
        KPIEnd[/api/kpi]
    end
    
    subgraph Operations [Operasyonlar]
        GET[GET - Listele/Getir]
        POST[POST - Oluştur]
        PUT[PUT - Güncelle]
        DELETE[DELETE - Sil]
    end
    
    subgraph Response [Yanıtlar]
        Success[200/201 Success]
        BadRequest[400 Bad Request]
        Unauthorized[401 Unauthorized]
        NotFound[404 Not Found]
        ServerError[500 Server Error]
    end
    
    Auth --> GET
    Auth --> POST
    
    Equip --> GET
    Equip --> POST
    Equip --> PUT
    Equip --> DELETE
    
    WO --> GET
    WO --> POST
    WO --> PUT
    
    Sensor --> GET
    Sensor --> POST
    
    KPIEnd --> GET
    
    GET --> Success
    POST --> Success
    PUT --> Success
    DELETE --> Success
    
    GET -.-> NotFound
    POST -.-> BadRequest
    PUT -.-> NotFound
    DELETE -.-> NotFound
    
    Auth -.-> Unauthorized
    
    GET -.-> ServerError
    POST -.-> ServerError
```

---

## Notlar:

- **ISO 55000**: Asset Management standardına uygun yapı
- **EN 15341**: Bakım KPI'ları standardına uyumlu metrikler
- **ISO 27001**: Güvenlik ve yetkilendirme kontrolleri
- **Sensör Verileri**: Real-time veri akışı ile Digital Twin konsepti
- **Otomatik İş Emirleri**: Bakım planlarından otomatik oluşturulma
- **Rol Tabanlı Erişim**: Admin, Manager, Technician, Operator rolleri
- **Traceability**: Tüm işlemler loglanır ve izlenebilir

