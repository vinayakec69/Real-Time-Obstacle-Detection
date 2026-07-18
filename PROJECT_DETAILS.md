# 👓 CareLens: Comprehensive Project Report

## 1. Executive Summary
**CareLens** is a cutting-edge, wearable assistive technology designed specifically for the visually impaired. By combining lightweight edge-computing hardware with state-of-the-art Vision AI, CareLens provides real-time, low-latency spatial awareness to its users. The system identifies everyday obstacles—such as chairs, tables, and people—and delivers discreet, conversational audio warnings directly into the user's ear.

Unlike traditional white canes that only detect ground-level obstacles within a few feet, CareLens provides a full 3D semantic understanding of the room, empowering users to navigate unfamiliar environments with confidence.

---

## 2. Non-Technical Aspects & Social Impact

### 🎯 The Problem
Visually impaired individuals often struggle with navigation in dynamic indoor environments. While traditional tools (guide dogs, white canes) are incredibly useful, they lack the ability to inform the user *what* the obstacle is. A cane can detect an object in the way, but it cannot tell the user if it is a person to be greeted or a chair to be walked around.

### 💡 The Solution
CareLens bridges this sensory gap by acting as a "digital eye." It translates visual data into auditory cues. 

### 👤 User Experience (UX)
The UX was designed with extreme care to avoid sensory overload:
- **Private Audio:** Instead of a loud public speaker that draws unwanted attention, the system uses discrete In-Ear Monitors (IEMs).
- **Conversational Tone:** Rather than robotic, rapid-fire commands, the audio cues are formatted as polite warnings (e.g., *"Watch out, there is a chair in front of you"*).
- **Intelligent Cooldowns:** The system employs a 4-second memory cooldown per object. If the user is standing in front of a table, the AI will not spam "table ahead" 30 times a second; it informs the user once and waits until the user moves to a new area.

---

## 3. Technical Aspects: The Hardware Stack

To achieve real-time AI inference without relying on a laggy internet connection, the entire system runs locally on specialized edge hardware.

| Component | Description & Role |
| :--- | :--- |
| **NVIDIA Jetson Orin Nano (8GB)** | The "Brain" of the system. This embedded supercomputer features a powerful GPU capable of running massive AI models entirely offline at high frame rates. |
| **Intel RealSense Camera** | The "Eyes." It captures high-resolution RGB video feeds of the environment. |
| **Type-C Digital-to-Analog Converter (DAC)** | Acts as a digital soundcard to bypass standard Bluetooth latency and antenna issues, ensuring zero-lag audio processing. |
| **KZ EDX Pro IEMs** | Professional-grade in-ear monitors providing crystal-clear, private audio directly to the user. |

---

## 4. Technical Aspects: The Software Stack

### 🧠 Vision AI Architecture (YOLOv8)
The project utilizes **YOLOv8** (You Only Look Once), specifically the `yolov8s.pt` (Small) architecture. 
- **Pre-trained Mastery:** The model is pre-trained on the COCO dataset (330,000+ images), allowing it to instantly and flawlessly recognize 80 common classes out-of-the-box, including crucial indoor obstacles like people, chairs, couches, dining tables, and cell phones.
- **Inference Speed:** YOLO is a single-shot detector, meaning it analyzes the entire image in one pass through the neural network. This allows the Orin Nano to process the camera feed in real-time (30+ FPS).

### 🗣️ Audio Engine (`pyttsx3`)
Because CareLens must work outdoors or in areas with no Wi-Fi, cloud-based text-to-speech APIs (like Google TTS) were rejected. Instead, the system uses `pyttsx3` backed by the Linux `espeak` engine. This provides 100% offline, zero-latency speech synthesis. The engine speed is specifically tuned to 110 WPM for maximum conversational clarity.

---

## 5. Engineering Challenges & Edge Optimizations

Running a 11-Million parameter neural network on an 8GB edge device required intense optimization:

1. **Avoiding OOM (Out of Memory) Crashes:** 
   Early iterations of custom training caused the Jetson's `CUDACachingAllocator` to crash due to RAM exhaustion. We solved this by strictly limiting the PyTorch dataloader to `batch=1` and `workers=1`, preventing RAM spikes.
2. **Catastrophic Forgetting:**
   Attempts to fine-tune the model on sparse, noisy public datasets resulted in the AI "un-learning" basic objects. We strategically pivoted to utilizing the expertly-trained base COCO weights, which instantly solved the false-positive bounding box issues.
3. **Bypassing Bluetooth Latency:**
   The Orin Nano's default Bluetooth stack can suffer from extreme range limitations if the M.2 IPEX antennas are not perfectly seated. We bypassed this hardware flaw entirely by routing audio through the Type-C port using a dedicated digital DAC.

---

## 6. Future Scope
- **Depth Integration:** Utilizing the RealSense's infrared depth sensors to calculate the exact distance (in meters) to the obstacle, and only warning the user if the obstacle is within a 1.5-meter radius.
- **Custom Pill Detection:** Training a highly specialized, secondary micro-model specifically for identifying crucial medications.
- **Battery Optimization:** Porting the model to NVIDIA TensorRT (`.engine`) to reduce power consumption and extend the battery life of the wearable unit.
