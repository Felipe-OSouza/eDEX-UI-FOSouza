class UpdateChecker {
    constructor() {
        // Update check desabilitado: este fork (security-patched) é a versão
        // mais recente disponível e o projeto original está arquivado.
        // O aviso de atualização foi removido para evitar falsos positivos.
        let electron = require("electron");
        electron.ipcRenderer.send("log", "info", "UpdateChecker: disabled (security-patched fork, no updates expected).");
    }
}

module.exports = {
    UpdateChecker
};
