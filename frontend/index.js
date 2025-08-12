      const form = document.getElementById("uploadForm");
      const imageInput = document.getElementById("imageInput");
      const previewImage = document.getElementById("previewImage");
      const resultsDiv = document.getElementById("results");
      const resultList = document.getElementById("resultList");

      await obterTamanhoDoBancoDedados();
      resultsDiv.classList.remove("hidden");
      resultList.innerHTML = "";


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
        formData.append("adicionarImgAoDb", addToIndex);

        const res = await fetch("/recognize", {
          method: "POST",
          body: formData,
        });

        const response = await res.json();
        resultsDiv.classList.remove("hidden");
        resultList.innerHTML = "";

        if (response.status === "success") {
          showSuccessToast(response.message);
          response.data.forEach((nome) => {
            const img = document.createElement("img");
            img.src = `/images/${nome}`;
            img.alt = nome;
            img.classList = "max-h-40"
            resultList.appendChild(img);
          });
        } else {
          resultList.innerHTML = `<p>${response.message}</p>`;
        }
        await obterTamanhoDoBancoDedados();
      });



      async function obterTamanhoDoBancoDedados(){
       const res = await fetch("/info", {
          method: "GET"
        });

        const response = await res.json();

        if (response.status === "success") {
          const quantidade = response.data.quantidade_rostos;
          const texto = `Número de fotos presentes nessa instância: ${quantidade}`;
          document.getElementById("quantidadeFotos").textContent = texto;
        }
      }

      function showSuccessToast(message = "Reconhecimento realizado com sucesso!") {
      const toast = document.getElementById("successToast");
      const toastText = document.getElementById("toastMessage");
      toastText.textContent = message;

      toast.classList.remove("hidden");
      const innerDiv = toast.querySelector("div");
      innerDiv.classList.remove("opacity-0", "translate-y-2");
      innerDiv.classList.add("opacity-100", "translate-y-0");

      setTimeout(() => {
        innerDiv.classList.add("opacity-0", "translate-y-2");
        innerDiv.classList.remove("opacity-100", "translate-y-0");

        setTimeout(() => {
          toast.classList.add("hidden");
        }, 300); 
      }, 3000);   
    }