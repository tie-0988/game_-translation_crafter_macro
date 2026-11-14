// Keep both upstream's pre-flight check and Trunk's Wasm loader pending while
// coi-serviceworker claims the page and reloads it with COOP/COEP headers.
window.coi = {
    coepCredentialless: () => false,
    coepDegrade: () => false,
};
window.raphaelIsolationReady = window.crossOriginIsolated === false
    ? new Promise(resolve => setTimeout(() => resolve(false), 15000))
    : Promise.resolve(true);
