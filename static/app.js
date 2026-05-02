console.log("JS已加载");

let allProducts = [];

/* 页面打开默认显示 Maquinas */
window.onload = function () {
    loadProducts();
};

/* 读取全部商品 */
function loadProducts() {

fetch("http://127.0.0.1:5000/products")
.then(function(res){
    return res.json();
})
.then(function(data){

    console.log("Datos:", data);

    allProducts = data;

    filterProducts("Maquinas");   // 默认显示 maquinas

})
.catch(function(err){
    console.error("Error:", err);
});

}

/* 分类筛选 */
function filterProducts(tipo){

const container = document.getElementById("products");

container.innerHTML = "";

const filtered = allProducts.filter(function(p){
    return p.tipo === tipo;
});

filtered.forEach(function(p){

    const card = document.createElement("div");
    card.className = "card";

    card.innerHTML = `
        <img src="${p.image}" />
        <h3>${p.name}</h3>
        <p>Precio: ${p.price}</p>
    `;

    card.addEventListener("click", function(){
        window.location.href = `product.html?id=${p.id}`;
    });

    container.appendChild(card);

});

}