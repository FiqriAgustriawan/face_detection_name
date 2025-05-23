import cv2
import numpy as np
import time
import os

def analyze_frame(frame):
    """Analisis frame untuk cek apakah benar-benar hitam atau bermasalah"""
    if frame is None:
        return "Frame kosong (None)"
    
    if frame.size == 0:
        return "Frame kosong (ukuran 0)"
    
    # Cek apakah frame benar-benar hitam
    black_threshold = 5  # Batas nilai untuk dianggap "hitam"
    is_black = np.mean(frame) < black_threshold
    
    # Cek apakah nilai piksel valid
    min_val = np.min(frame)
    max_val = np.max(frame)
    mean_val = np.mean(frame)
    
    result = f"Ukuran: {frame.shape}, Tipe: {frame.dtype}\n"
    result += f"Nilai: min={min_val}, max={max_val}, rata-rata={mean_val:.1f}\n"
    result += f"{'HITAM' if is_black else 'TIDAK HITAM'}"
    
    return result

def test_camera_enhanced():
    print("Tes kamera dengan diagnostik mendalam...")
    
    # Cek apakah folder output ada
    os.makedirs("camera_test_output", exist_ok=True)
    
    # Coba beberapa backend kamera
    backends = [
        (cv2.CAP_DSHOW, "DirectShow"),
        (cv2.CAP_MSMF, "Media Foundation"),
        (cv2.CAP_ANY, "Default")
    ]
    
    # Coba beberapa resolusi
    resolutions = [
        (640, 480, "640x480"),
        (320, 240, "320x240"),
        (800, 600, "800x600"),
        (1280, 720, "1280x720"),
        (0, 0, "Default")  # 0,0 berarti tidak mengatur resolusi
    ]
    
    for backend_id, backend_name in backends:
        print(f"\nMencoba backend: {backend_name} (ID: {backend_id})")
        
        # Coba buka kamera
        try:
            cap = cv2.VideoCapture(0, backend_id)
            
            if not cap.isOpened():
                print(f"  Gagal membuka kamera dengan {backend_name}")
                continue
                
            print(f"  Berhasil membuka kamera dengan {backend_name}")
            
            # Coba setiap resolusi
            for width, height, res_name in resolutions:
                if width > 0 and height > 0:
                    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
                    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
                    print(f"  Mencoba resolusi {res_name}...")
                else:
                    print(f"  Mencoba resolusi default...")
                
                # Baca beberapa frame (kadang frame pertama bermasalah)
                for i in range(10):
                    ret, frame = cap.read()
                    if ret:
                        break
                    time.sleep(0.1)
                
                if not ret:
                    print(f"  Gagal membaca frame dengan resolusi {res_name}")
                    continue
                
                # Analisis frame
                analysis = analyze_frame(frame)
                print(f"  Analisis frame: {analysis}")
                
                # Simpan frame untuk inspeksi
                output_file = f"camera_test_output/{backend_name.replace(' ', '_')}_{res_name}.jpg"
                cv2.imwrite(output_file, frame)
                print(f"  Frame disimpan ke {output_file}")
                
                # Coba tiga strategi tampilan berbeda
                display_methods = [
                    ("Normal", lambda f: f),
                    ("BGR->RGB", lambda f: cv2.cvtColor(f, cv2.COLOR_BGR2RGB)),
                    ("Enhanced", lambda f: cv2.convertScaleAbs(f, alpha=1.5, beta=30))
                ]
                
                for method_name, transform in display_methods:
                    try:
                        display_frame = transform(frame.copy())
                        window_name = f"Test - {backend_name} - {res_name} - {method_name}"
                        
                        print(f"  Menampilkan dengan metode: {method_name}")
                        print(f"  Tekan tombol apa saja untuk lanjut...")
                        
                        cv2.imshow(window_name, display_frame)
                        cv2.waitKey(0)
                        cv2.destroyWindow(window_name)
                    except Exception as e:
                        print(f"  Error dalam metode tampilan {method_name}: {str(e)}")
            
            # Tutup kamera
            cap.release()
            
        except Exception as e:
            print(f"  Error dengan backend {backend_name}: {str(e)}")
    
    cv2.destroyAllWindows()
    print("\nTes selesai. Periksa hasil di folder 'camera_test_output'")

if __name__ == "__main__":
    test_camera_enhanced()