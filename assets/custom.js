// assets/custom.js
function CustomCheckboxRenderer() {}
CustomCheckboxRenderer.prototype.init = function(params) {
    console.log('CustomCheckboxRenderer init:', params);
    this.eGui = document.createElement('input');
    this.eGui.type = 'checkbox';
    this.eGui.checked = params.value || false;
    this.eGui.addEventListener('change', function() {
        params.setValue(this.checked);
        console.log('Checkbox changed:', this.checked, 'Row:', params.data);
    });
};
CustomCheckboxRenderer.prototype.getGui = function() {
    return this.eGui;
};

// Инициализация глобального объекта для клиентовдских функций
document.addEventListener('DOMContentLoaded', function() {
    if (!window.dash_clientside) {
        window.dash_clientside = {};
    }
    window.dash_clientside.clientside = window.dash_clientside.clientside || {};

    // Обеспечение доступности dash_ag_grid
    if (typeof dash_ag_grid === 'undefined') {
        console.warn('dash_ag_grid is not defined, ensure it is loaded');
        return;
    }
});