import cv2

def test_camera_simple():
    print("Tes kamera sederhana...")
    
    # Coba beberapa backend kamera
    backends = [
        cv2.CAP_DSHOW,    # DirectShow (Windows)
        cv2.CAP_MSMF,     # Media Foundation (Windows)
        cv2.CAP_V4L2,     # Video4Linux (Linux)
        cv2.CAP_IMAGES,   # Images
        cv2.CAP_ANY       # Default
    ]
    
    for backend in backends:
        try:
            print(f"Mencoba backend {backend}...")
            
            # Tunggu sejenak sebelum membuka kamera
            import time
            time.sleep(1)
            
            # Buka kamera tanpa batasan tinggi/lebar
            cap = cv2.VideoCapture(0, backend)
            
            if not cap.isOpened():
                print(f"  Backend {backend} gagal membuka kamera")
                continue
                
            print(f"  Backend {backend} berhasil membuka kamera")
            
            # Ambil satu frame
            print("  Membaca frame...")
            ret, frame = cap.read()
            
            if not ret:
                print("  Gagal membaca frame")
                cap.release()
                continue
                
            print(f"  Berhasil membaca frame dengan ukuran {frame.shape}")
            
            # Simpan frame untuk verifikasi
            output_file = f"kamera_test_{backend}.jpg"
            cv2.imwrite(output_file, frame)
            print(f"  Frame disimpan ke {output_file}")
            
            # Tampilkan frame dan tunggu input keyboard
            print("  Menampilkan frame, tekan tombol apa saja untuk melanjutkan...")
            cv2.imshow("Tes Kamera", frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
            # Tutup kamera
            cap.release()
            
            print(f"Backend {backend} berfungsi dengan baik")
            return backend
            
        except Exception as e:
            print(f"  Error pada backend {backend}: {str(e)}")
    
    print("Semua backend gagal!")
    return None

if __name__ == "__main__":
    working_backend = test_camera_simple()
    if working_backend is not None:
        print(f"Gunakan backend {working_backend} untuk program utama Anda")
    else:
        print("Tidak ada backend kamera yang berfungsi")