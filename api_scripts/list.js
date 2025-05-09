const payload = {
    limit: 20,
    offset: 0,
    sceneTypeList: []
};

fetch("https://3d.hunyuan.tencent.com/api/3d/creations/list", {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "x-product": "hunyuan3d",
        "x-source": "web",
        "trace-id": crypto.randomUUID(),
        "cache-control": "no-cache",
        "content-type": "application/json",
        "date": new Date().toISOString(),
        "accept": "application/json, text/plain, */*",
        // Nota: no pongas cookies manualmente si estás en navegador y ya tienes sesión
    },
    body: JSON.stringify(payload),
    credentials: "include" // Usa cookies activas automáticamente
})
.then(res => res.json())
.then(data => {
    console.log("✅ List of assets:");
    console.log(data);
})
.catch(err => console.error("❌ Error:", err));