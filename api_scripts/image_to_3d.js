// 1. Mandar solicitud para generar modelo 3d a partir de prompt (texto).

const payload = {
  prompt: "Cat posing as a ninja in a samurai outfit, 3d model, highly detailed, photorealistic, 8k, octane render",
  title: "Cat posing as a ninja in a samurai outfit, 3d model, highly detailed, photorealistic, 8k, octane render", // lo mismo que prompt !!!!
  style: "", // "" por defecto, pero hay estilos como "china_style"... son presets... no poner cualquier cosa aquí heh
  sceneType: "playGround3D-2.0",
  modelType: "modelCreationV2.5",
  count: 4, // dejar en 4!
  enable_pbr: true, // opcional
  enableLowPoly: false // dejar así...
};

fetch("https://3d.hunyuan.tencent.com/api/3d/creations/generations", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "x-product": "hunyuan3d",
    "x-source": "web",
    "trace-id": crypto.randomUUID(),
    "accept": "application/json, text/plain, */*"
    // Nota: no pongas cookies manualmente si estás en navegador y ya tienes sesión
  },
  body: JSON.stringify(payload),
  credentials: "include" // Usa cookies activas automáticamente
})
.then(res => res.json())
.then(data => {
  // 2. Usar el id de la generación para obtener el metadata de la tarea.
  /*
  "https://3d.hunyuan.tencent.com/api/3d/creations/detail?creationsId={creationsId}"

  hacer un get a esa URL para obtener el metadata de la tarea.

  el metadata es un json con el siguiente formato:
  {
    "id": "0427cb78-890a-49a1-880c-bb67da6d53ea",
    "userId": "c58c0c817e8f4f94af8fe4cd6178473b",
    "env": "prod",
    "businessType": "text3d",
    "sceneType": "playGround3D-2.0",
    "modelType": "modelCreationV2.5",
    "prompt": "Stellar Blade character design, highly detailed. fit suit. perfect body. beautiful. semi-realistic. realistic proportions",
    "title": "Stellar Blade character design, highly detailed. fit suit. perfect body. beautiful. semi-realistic. realistic proportions",
    "style": "",
    "modelUrl3d": {},
    "n": 4,
    "status": "wait",
    "result": [
        {
            "assetId": "e1f9c882-ead9-4627-b720-d6eec64b298c",
            "status": "wait",
            "urlResult": {},
            "createdAt": 1746467976,
            "updatedAt": 1746467976
        },
        {
            "assetId": "3f4eab53-a72a-4e5c-a828-cb7fd0be7328",
            "status": "wait",
            "urlResult": {},
            "createdAt": 1746467976,
            "updatedAt": 1746467976
        },
        {
            "assetId": "db28aabd-8836-4f29-a1e0-6eb3ca145b04",
            "status": "wait",
            "urlResult": {},
            "createdAt": 1746467976,
            "updatedAt": 1746467976
        },
        {
            "assetId": "2f370037-7fea-4865-b66f-2d00faf87927",
            "status": "wait",
            "urlResult": {},
            "createdAt": 1746467976,
            "updatedAt": 1746467976
        }
    ],
    "waitNum": 60,
    "waitTime": 420,
    "createdAt": 1746467976,
    "updatedAt": 1746467976,
    "deletedAt": 0,
    "enable_pbr": true,
    "motionType": 0,
    "mesh": {}
  }
  */
  console.log("✅ Step 1: Generation Request Sent:", data);
  if (data && data.creationsId) {
    const creationsId = data.creationsId;
    console.log(`ℹ️ Extracted creationsId: ${creationsId}`);
    console.log("⏳ Step 2: Fetching creation details...");

    // Step 2: Fetch details using creationsId
    return fetch(`https://3d.hunyuan.tencent.com/api/3d/creations/detail?creationsId=${creationsId}`, {
      method: "GET",
      headers: {
        "x-product": "hunyuan3d",
        "x-source": "web",
        "trace-id": crypto.randomUUID(),
        "accept": "application/json, text/plain, */*"
        // Cookies handled by 'credentials: include'
      },
      credentials: "include" // Use active cookies automatically
    })
    .then(res => {
       if (!res.ok) {
         throw new Error(`HTTP error! status: ${res.status}`);
       }
       return res.json();
    })
    .then(details => {
      console.log("✅ Step 2: Creation Details Received:", details);
      // You can add further processing for the details here
      return details; // Pass details to the next .then if needed
    })
    .catch(err => {
        console.error("❌ Error fetching details (Step 2):", err);
        throw err; // Re-throw to be caught by the outer catch
    });
  } else {
    console.error("❌ Error: 'creationsId' not found in the response from Step 1.");
    throw new Error("'creationsId' not found");
  }
})
.catch(err => console.error("❌ Error in process:", err));

