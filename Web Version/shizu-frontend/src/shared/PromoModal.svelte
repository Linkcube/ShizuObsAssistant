<script>
    import {
        MaterialButton,
        MaterialInput,
        IconButton,
        MaterialSelect
    } from 'linkcube-svelte-components';
    import Modal from './Modal.svelte';
    import {
        fetchGetFilePath,
        currentLineup,
        lineups,
        fetchLineup,
        toFileName,
        fetchAddPromo,
        fetchUpdatePromo,
        fetchDeletePromo,

        fetchAddPromoToLineup

    } from '$lib/store.js';
    import { createEventDispatcher } from 'svelte';
    import { get } from 'svelte/store';

    const dispatch = createEventDispatcher();
    const close = () => dispatch('close');

    export let index = -1;
    export let name = "";
    export let file_path = "";

    const current_lineup = get(currentLineup);
    const lineup_names = get(lineups);
    let target_lineup = lineup_names[0];

    let file_name = toFileName(file_path);
    let selecting_file = false;

    function savePromo() {
        if (index < 0) {
            fetchAddPromo(name, file_path);
        } else {
            fetchUpdatePromo(
                index,
                name,
                file_path
            );
        }
        close();
    }

    function selectFile() {
        if (selecting_file) return;

        selecting_file = true;
        fetchGetFilePath().then(promise => {
            Promise.resolve(promise).then(response => {
                if (response.hasOwnProperty('data')) {
                    file_name = response.data.getFilePath[0];
                    file_path = response.data.getFilePath[1];
                }
            }).catch(() => console.log("Dialog closed"))
            .finally(() => selecting_file = false)
        });
    }

    function removePromo() {
        fetchDeletePromo(index).then(() => {
            if (current_lineup) fetchLineup(current_lineup)
        });
        close();
    }

    function addToLineup() {
        let lineup_name = current_lineup ? current_lineup : target_lineup;
        fetchAddPromoToLineup(lineup_name, name).then(_ => {
            if (current_lineup) fetchLineup(current_lineup)
        });
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

<Modal on:close={close} on:submission={savePromo}>
    <div class="central-column">
        <div class="row">
            <MaterialInput label="Promo Name" bind:value={name}/>
            {#if index >= 0}
                <div class="delete">
                    <IconButton icon="delete_forever" title="Delete Promo" on:click={removePromo} />
                </div>
            {/if}
        </div>
        <div class="row">
            <MaterialButton value="Select File" on:click={selectFile} />
            <label>{file_name}</label>
        </div>
        {#if index >= 0 && lineup_names.length != 0}
            <div class="row">
                <MaterialButton value="Add to{current_lineup ? ' current ' : ' '}Lineup" on:click={addToLineup} />
                {#if !current_lineup}
                    <MaterialSelect label="Lineups" bind:value={target_lineup}>
                        {#each lineup_names as name}
                            <option value={name}>{name}</option>
                        {/each}
                    </MaterialSelect>
                {/if}
            </div>
        {/if}
    </div>
</Modal>