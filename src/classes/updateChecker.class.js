class UpdateChecker {
    constructor() {
        // Update check desabilitado: fork security-patched é a versão
        // mais recente disponível. Projeto original está arquivado.
        let electron = require("electron");
        electron.ipcRenderer.send("log", "info", "UpdateChecker: disabled (security-patched fork, no updates expected).");
    }
}

module.exports = {
    UpdateChecker
};
