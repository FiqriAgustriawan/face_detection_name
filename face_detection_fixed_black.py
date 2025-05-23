import cv2
import numpy as np
import time
import os

def detect_faces_with_enhanced_display():
    print("Memulai deteksi wajah dengan penanganan layar hitam...")
    
    # Buat direktori untuk sampel wajah
    os.makedirs("face_samples", exist_ok=True)
    
    # Load detektor wajah
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Coba dengan DirectShow (biasanya paling stabil di Windows)
    print("Membuka kamera dengan DirectShow...")
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    
    # Terapkan pengaturan kamera yang konservatif
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Tunggu sejenak agar kamera siap
    time.sleep(2)
    
    if not cap.isOpened():
        print("Gagal membuka kamera!")
        return
    
    # Tingkatkan kontras dan kecerahan default untuk mengatasi layar hitam
    brightness_adjustment = 30  # Tambahkan nilai ke setiap piksel
    contrast_adjustment = 1.5   # Kalikan setiap piksel dengan nilai ini
    
    # Counter untuk sampel wajah
    sample_count = 0
    max_samples = 30
    last_sample_time = time.time()
    
    # Loop utama
    print("Deteksi wajah dimulai. Tekan 'q' untuk keluar, 'b'/'c' untuk menyesuaikan kecerahan/kontras")
    while True:
        # Baca frame dari webcam
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print("Gagal membaca frame!")
            time.sleep(0.5)
            continue
        
        # SOLUSI UNTUK LAYAR HITAM: Tingkatkan kontras dan kecerahan
        enhanced_frame = cv2.convertScaleAbs(frame, alpha=contrast_adjustment, beta=brightness_adjustment)
        
        # Konversi ke grayscale untuk deteksi wajah
        gray = cv2.cvtColor(enhanced_frame, cv2.COLOR_BGR2GRAY)
        
        # Deteksi wajah
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Buat salinan frame untuk ditampilkan
        display_frame = enhanced_frame.copy()
        
        # Gambar kotak dan hitung
        face_count = len(faces)
        
        # Jika ada wajah terdeteksi, ambil sampel
        for (x, y, w, h) in faces:
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Ambil sampel wajah jika sudah waktunya
            current_time = time.time()
            if sample_count < max_samples and current_time - last_sample_time > 0.5:
                face_sample = gray[y:y+h, x:x+w]
                sample_file = f"face_samples/face_{sample_count}.jpg"
                cv2.imwrite(sample_file, face_sample)
                sample_count += 1
                last_sample_time = current_time
        
        # Tampilkan informasi tentang nilai piksel untuk diagnosa
        avg_brightness = np.mean(enhanced_frame)
        
        # Tampilkan jumlah wajah dan info diagnosis
        cv2.putText(display_frame, f'Wajah terdeteksi: {face_count}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(display_frame, f'Sampel: {sample_count}/{max_samples}', (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(display_frame, f'Kecerahan: {brightness_adjustment}, Kontras: {contrast_adjustment:.1f}', (10, 90), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(display_frame, f'Rata-rata piksel: {avg_brightness:.1f}', (10, 120), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Tampilkan frame yang telah diproses
        cv2.imshow('Deteksi Wajah (Enhanced)', display_frame)
        
        # Kontrol dengan keyboard
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            # Keluar
            break
        elif key == ord('b'):
            # Tingkatkan kecerahan
            brightness_adjustment += 10
            print(f"Kecerahan disesuaikan ke: {brightness_adjustment}")
        elif key == ord('c'):
            # Tingkatkan kontras
            contrast_adjustment += 0.2
            print(f"Kontras disesuaikan ke: {contrast_adjustment:.1f}")
        elif key == ord('B'):
            # Kurangi kecerahan
            brightness_adjustment -= 10
            print(f"Kecerahan disesuaikan ke: {brightness_adjustment}")
        elif key == ord('C'):
            # Kurangi kontras
            contrast_adjustment -= 0.2
            contrast_adjustment = max(0.1, contrast_adjustment)  # Jangan sampai negatif
            print(f"Kontras disesuaikan ke: {contrast_adjustment:.1f}")
        elif key == ord('r'):
            # Reset pengaturan
            brightness_adjustment = 30
            contrast_adjustment = 1.5
            print("Pengaturan direset")
    
    # Bersihkan sumber daya
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"Deteksi wajah selesai. {sample_count} sampel wajah disimpan.")

if __name__ == "__main__":
    detect_faces_with_enhanced_display()