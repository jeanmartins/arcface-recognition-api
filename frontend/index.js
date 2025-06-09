   const form = document.getElementById("uploadForm");
      const imageInput = document.getElementById("imageInput");
      const previewImage = document.getElementById("previewImage");
      const resultsDiv = document.getElementById("results");
      const resultList = document.getElementById("resultList");

      imageInput.addEventListener("change", () => {
        const file = imageInput.files[0];
        if (file) {
          const reader = new FileReader();
          reader.onload = (e) => {
            previewImage.src = e.target.result;
            previewImage.classList.remove("hidden");
          };
          reader.readAsDataURL(file);
        }
      });

      form.addEventListener("submit", async (e) => {
        e.preventDefault();
        resultList.innerHTML = "";
        const file = imageInput.files[0];
        const addToIndex = document.getElementById("addToIndex").checked;
        const k = document.getElementById("kValue").value;

        if (!file) return alert("Selecione uma imagem.");

        const formData = new FormData();
        formData.append("file", file);
        formData.append("k", k);
        formData.append("addToIndex", addToIndex);

        const res = await fetch("/recognize", {
          method: "POST",
          body: formData,
        });

        const data = await res.json();
        resultsDiv.classList.remove("hidden");
        resultList.innerHTML = "";

        if (Array.isArray(data)) {
          data.forEach((nome) => {
            const img = document.createElement("img");
            img.src = `/images/rostos_dataset/${nome}`;
            img.alt = nome;
            img.classList = "max-h-80"
            resultList.appendChild(img);
          });
        } else {
          resultList.innerHTML = `<p>${data}</p>`;
        }
      });