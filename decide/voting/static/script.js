console.log('Hola')

var select = document.getElementById("id_tipo");
var options = document.getElementById("options-group");

select.addEventListener('change',(e)=>{
    var value = e.target.value;
    if(value === 'B'){
        options.setAttribute('hidden','');
    }else if (value === 'O'){
        options.removeAttribute('hidden');
    }
});
