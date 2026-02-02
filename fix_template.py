#!/usr/bin/env python3
# Template'i düzenle - eski JavaScript'i yeni olanla değiştir

import re

file_path = r"c:\Users\ferki\Desktop\bozankaya_ssh_takip\templates\servis_durumu.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Eski script bölümünü bul ve değiştir
old_script = """<script>
    // Sistem ve Alt Sistem verilerini JavaScript'e aktar
    const sistemler_data = {
        {% for sistem_adi, alt_sistemler in sistemler.items() %}
    "{{ sistem_adi }}": [{% for alt in alt_sistemler %}"{{ alt }}"{ { ", " if not loop.last else "" } } {% endfor %}],
    {% endfor %}
    };

    // Form elemanlarını seç
    const statusSelect = document.getElementById('statusSelect');
    const sistemSelect = document.getElementById('sistemSelect');
    const altSistemSelect = document.getElementById('altSistemSelect');
    const aciklamaInput = document.getElementById('aciklamaInput');
    const servisDurumuForm = document.getElementById('servisDurumuForm');

    // Durum değiştiğinde çalışacak fonksiyon
    function updateFormFields() {
        const selectedStatus = statusSelect.value;

        if (selectedStatus === 'servis') {
            // Servis seçilirse: sistem/alt sistem/açıklama devre dışı ve opsiyonel
            sistemSelect.disabled = true;
            altSistemSelect.disabled = true;
            aciklamaInput.disabled = true;

            sistemSelect.removeAttribute('required');
            altSistemSelect.removeAttribute('required');
            aciklamaInput.removeAttribute('required');

            // Değerleri temizle
            sistemSelect.value = '';
            altSistemSelect.value = '';
            aciklamaInput.value = '';

        } else if (selectedStatus === 'servis_disi') {
            // Servis Dışı seçilirse: hepsi zorunlu ve aktif
            sistemSelect.disabled = false;
            altSistemSelect.disabled = false;
            aciklamaInput.disabled = false;

            sistemSelect.setAttribute('required', 'required');
            altSistemSelect.setAttribute('required', 'required');
            aciklamaInput.setAttribute('required', 'required');

        } else if (selectedStatus === 'isletme_disi') {
            // İşletme Kaynaklı Servis Dışı: sadece açıklama zorunlu, sistem/alt sistem devre dışı
            sistemSelect.disabled = true;
            altSistemSelect.disabled = true;
            aciklamaInput.disabled = false;

            sistemSelect.removeAttribute('required');
            altSistemSelect.removeAttribute('required');
            aciklamaInput.setAttribute('required', 'required');

            // Sistem/alt sistem değerlerini temizle
            sistemSelect.value = '';
            altSistemSelect.value = '';

        } else {
            // Seçim yapılmamışsa hepsi devre dışı
            sistemSelect.disabled = true;
            altSistemSelect.disabled = true;
            aciklamaInput.disabled = true;

            sistemSelect.removeAttribute('required');
            altSistemSelect.removeAttribute('required');
            aciklamaInput.removeAttribute('required');
        }
    }

    // Sistem seçildiğinde alt sistemleri güncelle
    function updateAltSistemler() {
        const selectedSistem = sistemSelect.value;

        // Alt Sistem dropdown'ını temizle
        altSistemSelect.innerHTML = '<option value="">Seçiniz</option>';

        if (selectedSistem && sistemler_data[selectedSistem]) {
            // Seçili sistemin alt sistemlerini ekle
            sistemler_data[selectedSistem].forEach(altSistem => {
                const option = document.createElement('option');
                option.value = altSistem;
                option.textContent = altSistem;
                altSistemSelect.appendChild(option);
            });
        }
    }

    // Event listeners
    statusSelect.addEventListener('change', updateFormFields);
    sistemSelect.addEventListener('change', updateAltSistemler);

    // Form gönderme sırasında validasyon
    servisDurumuForm.addEventListener('submit', function (e) {
        const selectedStatus = statusSelect.value;

        if (selectedStatus === 'servis_disi') {
            // Sistem ve alt sistem seçili mi kontrol et
            if (!sistemSelect.value) {
                e.preventDefault();
                alert('Servis Dışı durumunda Sistem seçimi zorunludur.');
                sistemSelect.focus();
                return false;
            }
            if (!altSistemSelect.value) {
                e.preventDefault();
                alert('Servis Dışı durumunda Alt Sistem seçimi zorunludur.');
                altSistemSelect.focus();
                return false;
            }
            if (!aciklamaInput.value.trim()) {
                e.preventDefault();
                alert('Servis Dışı durumunda Açıklama zorunludur.');
                aciklamaInput.focus();
                return false;
            }
        } else if (selectedStatus === 'isletme_disi') {
            // Sadece açıklama zorunlu
            if (!aciklamaInput.value.trim()) {
                e.preventDefault();
                alert('İşletme Kaynaklı Servis Dışı durumunda Açıklama zorunludur.');
                aciklamaInput.focus();
                return false;
            }
        }
    });

    // Sayfa yüklendiğinde form alanlarını sıfırla
    document.addEventListener('DOMContentLoaded', function () {
        updateFormFields();
    });
</script>"""

new_script = """<script>
    // Sistemler verisini JavaScript'e aktar
    const sistemler_data = {
        {% for sistem_adi, sistem_data in sistemler.items() %}
        "{{ sistem_adi }}": {
            "tedarikçiler": [{% for t in sistem_data.tedarikçiler %}"{{ t }}"{{ ", " if not loop.last else "" }}{% endfor %}],
            "alt_sistemler": [{% for a in sistem_data.alt_sistemler %}"{{ a }}"{{ ", " if not loop.last else "" }}{% endfor %}]
        }{{ ", " if not loop.last else "" }}
        {% endfor %}
    };

    const statusSelect = document.getElementById('statusSelect');
    const sistemSelect = document.getElementById('sistemSelect');
    const tedarikciSelect = document.getElementById('tedarikciSelect');
    const altSistemSelect = document.getElementById('altSistemSelect');
    const aciklamaInput = document.getElementById('aciklamaInput');
    const servisDurumuForm = document.getElementById('servisDurumuForm');

    function updateFormFields() {
        const selectedStatus = statusSelect.value;
        if (selectedStatus === 'servis') {
            sistemSelect.disabled = true;
            tedarikciSelect.disabled = true;
            altSistemSelect.disabled = true;
            aciklamaInput.disabled = true;
            [sistemSelect, tedarikciSelect, altSistemSelect, aciklamaInput].forEach(el => el.removeAttribute('required'));
            sistemSelect.value = '';
            tedarikciSelect.value = '';
            altSistemSelect.value = '';
            aciklamaInput.value = '';
        } else if (selectedStatus === 'servis_disi') {
            sistemSelect.disabled = false;
            tedarikciSelect.disabled = false;
            altSistemSelect.disabled = false;
            aciklamaInput.disabled = false;
            [sistemSelect, tedarikciSelect, altSistemSelect, aciklamaInput].forEach(el => el.setAttribute('required', 'required'));
        } else if (selectedStatus === 'isletme_disi') {
            sistemSelect.disabled = true;
            tedarikciSelect.disabled = true;
            altSistemSelect.disabled = true;
            aciklamaInput.disabled = false;
            [sistemSelect, tedarikciSelect, altSistemSelect].forEach(el => el.removeAttribute('required'));
            aciklamaInput.setAttribute('required', 'required');
            sistemSelect.value = '';
            tedarikciSelect.value = '';
            altSistemSelect.value = '';
        } else {
            sistemSelect.disabled = true;
            tedarikciSelect.disabled = true;
            altSistemSelect.disabled = true;
            aciklamaInput.disabled = true;
            [sistemSelect, tedarikciSelect, altSistemSelect, aciklamaInput].forEach(el => el.removeAttribute('required'));
        }
    }

    function updateTedarikçiler() {
        const selectedSistem = sistemSelect.value;
        tedarikciSelect.innerHTML = '<option value="">Seçiniz</option>';
        altSistemSelect.innerHTML = '<option value="">Seçiniz</option>';
        if (selectedSistem && sistemler_data[selectedSistem]) {
            sistemler_data[selectedSistem].tedarikçiler.forEach(tedarikci => {
                const option = document.createElement('option');
                option.value = tedarikci;
                option.textContent = tedarikci;
                tedarikciSelect.appendChild(option);
            });
        }
    }

    function updateAltSistemler() {
        const selectedSistem = sistemSelect.value;
        altSistemSelect.innerHTML = '<option value="">Seçiniz</option>';
        if (selectedSistem && sistemler_data[selectedSistem]) {
            sistemler_data[selectedSistem].alt_sistemler.forEach(altSistem => {
                const option = document.createElement('option');
                option.value = altSistem;
                option.textContent = altSistem;
                altSistemSelect.appendChild(option);
            });
        }
    }

    statusSelect.addEventListener('change', updateFormFields);
    sistemSelect.addEventListener('change', () => {
        updateTedarikçiler();
        updateAltSistemler();
    });

    servisDurumuForm.addEventListener('submit', function(e) {
        const selectedStatus = statusSelect.value;
        if (selectedStatus === 'servis_disi') {
            if (!sistemSelect.value || !tedarikciSelect.value || !altSistemSelect.value || !aciklamaInput.value.trim()) {
                e.preventDefault();
                alert('Servis Dışı durumunda tüm alanlar zorunludur.');
                return false;
            }
        } else if (selectedStatus === 'isletme_disi') {
            if (!aciklamaInput.value.trim()) {
                e.preventDefault();
                alert('İşletme Kaynaklı Servis Dışı durumunda Açıklama zorunludur.');
                aciklamaInput.focus();
                return false;
            }
        }
    });

    document.addEventListener('DOMContentLoaded', function() {
        updateFormFields();
    });
</script>"""

content = content.replace(old_script, new_script)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Template güncellendi!")
