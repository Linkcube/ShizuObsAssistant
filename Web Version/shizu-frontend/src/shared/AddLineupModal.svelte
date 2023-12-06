<script>
    import {
        MaterialInput
    } from 'linkcube-svelte-components';
    import Modal from './Modal.svelte';
    import { 
        fetchCreateLineup, fetchLineups
    } from '$lib/store.js';
    import { createEventDispatcher } from 'svelte';

    const dispatch = createEventDispatcher();
    const close = () => dispatch('close');

    let name = "";

    function createLineup() {
        fetchCreateLineup(name).then(_ => fetchLineups());
        close();
    }

</script>

<Modal on:close={close} on:submission={createLineup}>
    <MaterialInput label="Lineup Name" bind:value={name} />
</Modal>