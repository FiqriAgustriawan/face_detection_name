import cv2
import numpy as np
import time
import os

def create_face_recognizer():
    # Buat direktori untuk menyimpan sampel wajah jika belum ada
    if not os.path.exists('face_samples'):
        os.makedirs('face_samples')
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    # Coba muat model jika sudah ada
    try:
        recognizer.read('face_model.yml')
        print("Model pengenal wajah dimuat!")
        return recognizer, True
    except:
        print("Tidak ada model pengenal wajah yang ditemukan.")
        return recognizer, False

def collect_face_samples(name):
    # Fungsi untuk mengumpulkan sampel wajah untuk pengenalan
    print(f"Mengumpulkan sampel wajah untuk {name}...")
    
    # Coba menggunakan berbagai backend kamera
    for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            print(f"Berhasil membuka kamera dengan backend {backend}")
            break
    
    if not cap.isOpened():
        print("Tidak dapat membuka kamera dengan backend manapun!")
        return False
    
    # Tunggu sebentar agar kamera siap
    time.sleep(2)
    
    # Muat detektor wajah
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    count = 0
    max_samples = 30
    
    print("Pengambilan sampel dimulai. Posisikan wajah Anda di depan kamera.")
    print(f"Akan mengambil {max_samples} sampel. Tekan ESC untuk batal.")
    
    sample_start = time.time()
    
    while count < max_samples:
        ret, frame = cap.read()
        
        if not ret:
            print("Gagal membaca frame!")
            continue
        
        # Buat salinan frame untuk ditampilkan
        display_frame = frame.copy()
        
        # Konversi ke grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Deteksi wajah
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        for (x, y, w, h) in faces:
            # Gambar kotak pada wajah
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # Hanya ambil sampel setiap 0.5 detik
            if time.time() - sample_start > 0.5:
                # Simpan potongan wajah
                face_sample = gray[y:y+h, x:x+w]
                sample_file = f"face_samples/{name}_{count}.jpg"
                cv2.imwrite(sample_file, face_sample)
                count += 1
                print(f"Mengambil sampel {count}/{max_samples}")
                sample_start = time.time()
        
        # Tampilkan progres
        cv2.putText(display_frame, f"Sampel: {count}/{max_samples}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Tampilkan frame
        cv2.imshow("Pengambilan Sampel Wajah", display_frame)
        
        # Keluar jika ESC ditekan
        if cv2.waitKey(1) & 0xFF == 27:  # ESC key
            break
    
    cap.release()
    cv2.destroyAllWindows()
    
    print(f"Pengambilan sampel selesai. {count} sampel diambil.")
    return count > 10  # minimal 10 sampel untuk pengenalan yang baik

def train_recognizer():
    print("Melatih model pengenalan wajah...")
    
    # Cek direktori sampel
    if not os.path.exists('face_samples'):
        print("Tidak ada direktori sampel wajah!")
        return False
    
    # Buat recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    # Siapkan data pelatihan
    faces = []
    labels = []
    label_info = {}
    next_label = 0
    
    # Baca semua sampel
    for file in os.listdir('face_samples'):
        if file.endswith('.jpg'):
            name = file.split('_')[0]
            
            # Beri label untuk setiap nama
            if name not in label_info:
                label_info[name] = next_label
                next_label += 1
            
            label = label_info[name]
            
            # Muat gambar
            img_path = os.path.join('face_samples', file)
            face_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            
            if face_img is not None:
                faces.append(face_img)
                labels.append(label)
    
    if len(faces) < 10:
        print("Tidak cukup sampel wajah untuk pelatihan!")
        return False
    
    # Latih model
    recognizer.train(faces, np.array(labels))
    
    # Simpan model
    recognizer.save('face_model.yml')
    
    # Simpan informasi label
    with open('label_info.txt', 'w') as f:
        for name, label in label_info.items():
            f.write(f"{name},{label}\n")
    
    print(f"Model dilatih dengan {len(faces)} sampel dari {len(label_info)} orang")
    return True

def load_label_info():
    label_info = {}
    
    try:
        with open('label_info.txt', 'r') as f:
            for line in f:
                name, label = line.strip().split(',')
                label_info[int(label)] = name
    except:
        pass
    
    return label_info

def face_recognition_system():
    print("Memulai sistem pengenalan wajah...")
    
    # Buat atau muat recognizer
    recognizer, model_exists = create_face_recognizer()
    
    # Jika tidak ada model, buat yang baru
    if not model_exists:
        print("Tidak ada model pengenalan wajah yang ditemukan.")
        print("Mari tambahkan wajah pertama ke sistem.")
        name = input("Masukkan nama Anda: ")
        
        if collect_face_samples(name):
            print("Sampel wajah terkumpul. Melatih model...")
            train_recognizer()
        else:
            print("Gagal mengumpulkan sampel wajah!")
            return
    
    # Muat informasi label
    label_info = load_label_info()
    if not label_info:
        print("Tidak dapat memuat informasi label!")
        return
    
    # Muat recognizer lagi dengan model yang sudah dilatih
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('face_model.yml')
    
    # Cari backend kamera yang berfungsi
    print("Membuka kamera...")
    camera_opened = False
    
    for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY]:
        print(f"Mencoba backend kamera {backend}...")
        cap = cv2.VideoCapture(0, backend)
        if cap.isOpened():
            # Tunggu sebentar agar kamera siap
            time.sleep(2)
            
            # Tes baca frame
            ret, test_frame = cap.read()
            if ret and test_frame is not None and test_frame.size > 0:
                print(f"Berhasil membuka kamera dengan backend {backend}")
                camera_opened = True
                break
            else:
                print(f"Backend {backend} terbuka tetapi tidak bisa membaca frame")
                cap.release()
        else:
            print(f"Tidak bisa membuka kamera dengan backend {backend}")
    
    if not camera_opened:
        print("Tidak dapat membuka kamera dengan backend manapun!")
        return
    
    # Set properti kamera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Muat detektor wajah
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    print("Sistem pengenalan wajah berjalan. Tekan 'q' untuk keluar, 'a' untuk tambah wajah baru.")
    
    while True:
        ret, frame = cap.read()
        
        if not ret or frame is None or frame.size == 0:
            print("Gagal membaca frame. Mencoba lagi...")
            time.sleep(0.5)
            continue
        
        # Konversi ke grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Deteksi wajah
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )
        
        # Proses setiap wajah
        for (x, y, w, h) in faces:
            # Potong bagian wajah
            face_roi = gray[y:y+h, x:x+w]
            
            # Prediksi wajah
            try:
                label, confidence = recognizer.predict(face_roi)
                
                # Tentukan nama berdasarkan label
                if confidence < 100:  # Ambang batas kepercayaan
                    name = label_info.get(label, "Unknown")
                    confidence_text = f"{confidence:.1f}%"
                else:
                    name = "Unknown"
                    confidence_text = "Low"
                
                # Warna kotak berdasarkan kepercayaan
                if confidence < 65:
                    box_color = (0, 255, 0)  # Hijau untuk kepercayaan tinggi
                elif confidence < 85:
                    box_color = (0, 255, 255)  # Kuning untuk kepercayaan sedang
                else:
                    box_color = (0, 0, 255)  # Merah untuk kepercayaan rendah
                
                # Gambar kotak dan nama
                cv2.rectangle(frame, (x, y), (x+w, y+h), box_color, 2)
                cv2.putText(frame, name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)
                cv2.putText(frame, confidence_text, (x+w-70, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, box_color, 1)
                
            except:
                # Jika ada error dalam pengenalan
                cv2.rectangle(frame, (x, y), (x+w, y+h), (128, 128, 128), 2)
                cv2.putText(frame, "Error", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
        
        # Tampilkan jumlah wajah
        cv2.putText(frame, f'Wajah terdeteksi: {len(faces)}', (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Tampilkan frame
        cv2.imshow('Sistem Pengenalan Wajah', frame)
        
        # Baca input keyboard
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            # Keluar dari program
            break
            
        elif key == ord('a'):
            # Tambah wajah baru
            cap.release()
            cv2.destroyAllWindows()
            
            name = input("Masukkan nama untuk wajah baru: ")
            if collect_face_samples(name):
                train_recognizer()
                
                # Muat ulang recognizer dan label
                recognizer = cv2.face.LBPHFaceRecognizer_create()
                recognizer.read('face_model.yml')
                label_info = load_label_info()
                
                # Buka kamera lagi
                cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                time.sleep(1)
    
    # Bersihkan sumber daya
    cap.release()
    cv2.destroyAllWindows()

# Start the system
if __name__ == "__main__":
    try:
        face_recognition_system()
    except Exception as e:
        print(f"Terjadi kesalahan: {str(e)}")