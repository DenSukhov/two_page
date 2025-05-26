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