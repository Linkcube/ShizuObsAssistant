<script>
    import {
        MaterialButton,
        MaterialInput,
        IconButton,
        MaterialSelect
    } from 'linkcube-svelte-components';
    import Modal from './Modal.svelte';
    import { 
        fetchAddDj,
        fetchGetFilePath,
        fetchUpdateDj,
        fetchDeleteDj,
        RTMP_SERVERS,
        currentLineup,
        lineups,
        fetchAddDjToLineup,
        fetchLineup,

        toFileName

    } from '$lib/store.js';
    import { createEventDispatcher } from 'svelte';
    import { get } from 'svelte/store';

    export let index = -1;
    export let name = "";
    export let logo_path = "";
    let logo_name = toFileName(logo_path);
    export let rtmp_server = "";
    export let stream_key = "";
    export let recording_path = "";
    let recording_name = toFileName(recording_path);
    let selecting_file = false;

    const current_lineup = get(currentLineup);
    const lineup_names = get(lineups);
    let target_lineup = lineup_names[0];


    const dispatch = createEventDispatcher();
    const close = () => dispatch('close');

    function saveDj() {
        if (index < 0) {
            fetchAddDj(
                name,
                logo_path,
                recording_path,
                rtmp_server,
                stream_key
            )
        } else {
            fetchUpdateDj(
                index,
                name,
                logo_path,
                recording_path,
                rtmp_server,
                stream_key
            )
        }
        close();
    }

    function selectLogo() {
        if (selecting_file) return;

        selecting_file = true;
        fetchGetFilePath().then(promise => {
            Promise.resolve(promise).then(response => {
                if (response.hasOwnProperty('data')) {
                    logo_name = response.data.getFilePath[0];
                    logo_path = response.data.getFilePath[1];
                }
            }).catch(() => console.log("Dialog closed"))
            .finally(() => selecting_file = false)
        });
    }

    function selectRecording() {
        if (selecting_file) return;

        selecting_file = true;
        fetchGetFilePath().then(promise => {
            Promise.resolve(promise).then(response => {
                if (response.hasOwnProperty('data')) {
                    recording_name = response.data.getFilePath[0];
                    recording_path = response.data.getFilePath[1];
                }
            }).catch(() => console.log("Dialog closed"))
            .finally(() => selecting_file = false)
        });
    }

    function removeDj() {
        fetchDeleteDj(index).then(() => {
            if (current_lineup) fetchLineup(current_lineup)
        });
        close();
    }

    function addToLineup() {
        let lineup_name = current_lineup ? current_lineup : target_lineup;
        fetchAddDjToLineup(lineup_name, name).then(_ => {
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

    .icon-container {
        margin-top: 10px;
        margin-right: 10px;
    }
</style>

<Modal on:close={close} on:submission={saveDj}>
    <div class="central-column">
        <div class="row">
            <MaterialInput label="DJ Name" bind:value={name}/>
            {#if index >= 0}
                <div class="delete">
                    <IconButton icon="delete_forever" title="Delete DJ" on:click={removeDj} />
                </div>
            {/if}
        </div>
        <div class="row">
            <div class="icon-container">
                <IconButton icon="photo" title="Select Logo" on:click={selectLogo} />
            </div>
            <!-- <MaterialButton value="Select Logo" on:click={selectLogo} /> -->
            <p>Logo: {logo_name ? logo_name : "Not Set"}</p>
        </div>
        <div class="row">
            <MaterialSelect label="RTMP Server" bind:value={rtmp_server}>
                {#each RTMP_SERVERS as { id, name}}
                    <option value={id}>{name}</option>
                {/each}
            </MaterialSelect>
            <MaterialInput label="Stream Key" bind:value={stream_key} />
        </div>
        <div class="row">
            <div class="icon-container">
                <IconButton icon="photo" title="Select Recording" on:click={selectRecording} />
            </div>
            <!-- <MaterialButton value="Select Recording" on:click={selectRecording} /> -->
            <p>Recording: {recording_name ? recording_name : "Not Set"}</p>
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