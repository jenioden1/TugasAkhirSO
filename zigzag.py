<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DCT Steganografi + Clipdrop</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 min-h-screen flex flex-col items-center p-6">
  <div class="w-full max-w-4xl bg-white shadow-xl rounded-2xl p-6">
    <h1 class="text-2xl font-bold mb-6 text-center text-indigo-700">🧠 DCT Steganografi + 🎨 Clipdrop</h1>

    <!-- Tab Menu -->
    <div class="flex justify-center mb-6 space-x-4">
      <button id="tabEmbed" onclick="showTab('embed')" class="px-4 py-2 bg-indigo-600 text-white rounded-lg">Embed Pesan</button>
      <button id="tabExtract" onclick="showTab('extract')" class="px-4 py-2 bg-gray-300 text-gray-800 rounded-lg">Ekstrak Pesan</button>
    </div>

    <!-- Embed Section -->
    <!-- Replace bagian EMBED TAB -->
<!-- Embed Section -->
<!-- EMBED SECTION -->
<div id="embedTab" class="space-y-6">

    <!-- Gambar Hasil Generate -->
    <div class="text-center">
      <h2 class="font-semibold mb-2 text-indigo-700">Gambar Hasil Generate</h2>
      <img id="resultImg" class="rounded-xl shadow-md max-w-full mx-auto hidden" />
      <div id="loading" class="text-sm text-gray-500 mt-2 hidden animate-pulse">⏳ Sedang generate gambar...</div>
    </div>
  
    <!-- Input Pesan Rahasia -->
    <div>
      <label class="block mb-1 font-semibold text-gray-700">Pesan rahasia</label>
      <textarea id="text" class="w-full p-3 border rounded-lg" rows="3" placeholder="Tulis pesan rahasiamu..."></textarea>
      <button onclick="embedTextIntoImage()" class="mt-2 bg-pink-600 hover:bg-pink-700 text-white px-4 py-2 rounded-lg">Embed ke Gambar</button>
    </div>
  
    <!-- Gambar Setelah Embed -->
    <div class="text-center">
      <h2 class="font-semibold mb-2 text-pink-700">Gambar Setelah Embed</h2>
      <canvas id="canvas" class="rounded-xl shadow-md mx-auto max-w-full hidden"></canvas>
    </div>
  
    <!-- TOAST NOTIFIKASI -->
    <div id="popup" class="fixed bottom-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg hidden z-50 transition-opacity duration-300">
      ✅ Pesan berhasil disisipkan ke dalam gambar!
    </div>
  </div>
  
  

    <!-- Extract Section -->
    <div id="extractTab" class="hidden">
      <div class="mb-4">
        <label class="block mb-1 font-semibold text-gray-700">Upload gambar untuk ekstrak pesan</label>
        <input type="file" id="uploadImage" accept="image/*" class="mb-2" />
        <button onclick="extractFromUploadedImage()" class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg">Extract Pesan</button>
      </div>
      <canvas id="uploadCanvas" class="hidden mt-4 max-w-full mx-auto"></canvas>
      <div id="extractedMessage" class="mt-4 p-4 bg-gray-100 border border-gray-300 rounded-lg hidden text-gray-800 text-sm"></div>
    </div>
  </div>

  <script>
    const apiKey = '4e7a6d4f38c295eeb000c7f45f0797e0bf7bf1adbf9357c4bd25712188d202047b3fb337e3e1df5ce31fa7b5a28f1d2b';

    function showTab(tab) {
      document.getElementById('embedTab').classList.toggle('hidden', tab !== 'embed');
      document.getElementById('extractTab').classList.toggle('hidden', tab !== 'extract');
      document.getElementById('tabEmbed').classList.toggle('bg-indigo-600', tab === 'embed');
      document.getElementById('tabExtract').classList.toggle('bg-indigo-600', tab === 'extract');
      document.getElementById('tabEmbed').classList.toggle('bg-gray-300', tab !== 'embed');
      document.getElementById('tabExtract').classList.toggle('bg-gray-300', tab !== 'extract');
      document.getElementById('tabEmbed').classList.toggle('text-white', tab === 'embed');
      document.getElementById('tabExtract').classList.toggle('text-white', tab === 'extract');
    }

    async function generateImageFromPrompt() {
        const prompt = document.getElementById('prompt').value;
        const formData = new FormData();
        formData.append("prompt", prompt);

        const loading = document.getElementById('loading');
        const resultImg = document.getElementById('resultImg');
        loading.classList.remove('hidden');
        resultImg.classList.add('hidden');

        const response = await fetch("https://clipdrop-api.co/text-to-image/v1", {
            method: "POST",
            headers: { "x-api-key": apiKey },
            body: formData
        });

        const blob = await response.blob();
        const base64 = await blobToBase64(blob);

        resultImg.src = base64;
        resultImg.classList.remove('hidden');
        loading.classList.add('hidden');
        }


        function embedTextIntoImage() {
  const canvas = document.getElementById('canvas');
  const ctx = canvas.getContext('2d');
  const resultImg = document.getElementById('resultImg');
  const text = document.getElementById('text').value;

  if (!resultImg.src) return alert("Harap generate gambar terlebih dahulu!");

  const img = new Image();
  img.src = resultImg.src;

  img.onload = () => {
    canvas.width = img.width;
    canvas.height = img.height;
    ctx.drawImage(img, 0, 0);

    const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const binaryMsg = toBinary(text + '|');
    const data = imageData.data;
    let msgIndex = 0;

    for (let i = 0; i < data.length && msgIndex < binaryMsg.length; i += 4) {
      data[i + 2] = (data[i + 2] & 0xFE) | parseInt(binaryMsg[msgIndex]);
      msgIndex++;
    }

    ctx.putImageData(imageData, 0, 0);
    canvas.classList.remove("hidden");

    // Tampilkan popup (toast)
    showPopup();
  }
}


    function extractFromUploadedImage() {
      const fileInput = document.getElementById('uploadImage');
      const canvas = document.getElementById('uploadCanvas');
      const ctx = canvas.getContext('2d');
      const file = fileInput.files[0];
      if (!file) return alert("Pilih gambar terlebih dahulu!");

      const reader = new FileReader();
      reader.onload = function () {
        const img = new Image();
        img.src = reader.result;
        img.onload = function () {
          canvas.width = img.width;
          canvas.height = img.height;
          ctx.drawImage(img, 0, 0);

          const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
          const data = imageData.data;
          let binary = '';
          for (let i = 0; i < data.length; i += 4) {
            binary += (data[i + 2] & 1).toString();
          }

          let chars = [];
          for (let i = 0; i < binary.length; i += 8) {
            const byte = binary.slice(i, i + 8);
            const char = String.fromCharCode(parseInt(byte, 2));
            if (char === '|') break;
            chars.push(char);
          }

          const message = chars.join('');
          document.getElementById('extractedMessage').textContent = message;
          document.getElementById('extractedMessage').classList.remove('hidden');
          canvas.classList.remove('hidden');
        };
      };
      reader.readAsDataURL(file);
    }

    function toBinary(str) {
      return str.split('').map(char =>
        char.charCodeAt(0).toString(2).padStart(8, '0')
      ).join('').split('');
    }

    function blobToBase64(blob) {
      return new Promise(resolve => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result);
        reader.readAsDataURL(blob);
      });
    }

    function showPopup() {
  const popup = document.getElementById('popup');
  popup.classList.remove('hidden');
  popup.classList.add('opacity-100');
  setTimeout(() => {
    popup.classList.add('hidden');
    popup.classList.remove('opacity-100');
  }, 3000);
}

  </script>
</body>
</html>
