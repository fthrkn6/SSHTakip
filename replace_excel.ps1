
# PowerShell script to replace Excel file
$oldFile = 'c:\Users\ferki\Desktop\bozankaya_ssh_takip\logs\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'
$newName = 'c:\Users\ferki\Desktop\bozankaya_ssh_takip\logs\ariza_listesi\Ariza_Listesi_BELGRAD_old.xlsx'
$tempFile = 'C:\Users\ferki\AppData\Local\Temp\Ariza_Listesi_BELGRAD_edit.xlsx'
$newFile = 'c:\Users\ferki\Desktop\bozankaya_ssh_takip\logs\ariza_listesi\Ariza_Listesi_BELGRAD.xlsx'

try {
    # Rename old file
    Rename-Item $oldFile $newName -Force -ErrorAction Stop
    Write-Host "✅ Eski dosya yeniden adlandırıldı"
    
    # Copy temp to original location
    Copy-Item $tempFile $newFile -Force
    Write-Host "✅ Güncellenmiş dosya kopyalandı"
    
    # Remove temp and old
    Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
    Remove-Item $newName -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Başarılı!"
    
} catch {
    Write-Host "❌ Hata: $_"
}
