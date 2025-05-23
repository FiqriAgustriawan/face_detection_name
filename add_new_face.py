import cv2
from face_recognition_complete import collect_face_samples, train_recognizer

def add_new_face():
    name = input("Masukkan nama untuk wajah baru: ")
    
    # Mengumpulkan sampel wajah
    success = collect_face_samples(name)
    
    if success:
        # Melatih ulang model dengan sampel baru
        train_recognizer()
        print(f"Wajah {name} berhasil ditambahkan!")
    else:
        print("Gagal mengumpulkan sampel wajah.")

if __name__ == "__main__":
    add_new_face()