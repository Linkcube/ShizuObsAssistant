<script>
    import {
        IconButton
    } from 'linkcube-svelte-components';
    import Modal from './Modal.svelte';
    import { 
        fetchLineup,
        ledger,
        toFileName,
        fetchRemoveLineupPromo
    } from '$lib/store.js';
    import { createEventDispatcher } from 'svelte';
    import { get } from 'svelte/store';

    export let index = 0;
    export let current_lineup = "";
    export let name = "";

    const ledger_data = get(ledger);
    const promo_data = ledger_data.promos.filter(promo => promo.name === name)[0];

    let file_name = toFileName(promo_data.path);

    const dispatch = createEventDispatcher();
    const close = () => dispatch('close');

    export const removeDj = () => {
        fetchRemoveLineupPromo(current_lineup, index).then(_ => fetchLineup(current_lineup));
        close();
    }
</script>

<style>
    .central-column {
        display: flex;
        flex-direction: column;
    }

    .row {
        display: flex;
        flex-direction: row;
    }

    .delete {
        margin-left: auto;
        --secondary-text-color: var(--delete-color, red);
    }
</style>

<Modal on:close={close} use_submission={false}>
    <div class="central-column">
        <div class="row">
            <p>Name: {name}</p>
            <div class="delete">
                <IconButton icon="delete" title="Remove from lineup" on:click={removeDj} />
            </div>
        </div>
        <div class="row">
            <p>Promo File: {file_name ? file_name : "Not Set"}</p>
        </div>
    </div>
</Modal>