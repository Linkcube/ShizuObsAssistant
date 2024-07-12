<script>
    import { createEventDispatcher } from 'svelte';
    import {
        error_stack
    } from '$lib/store';
    import Modal from './Modal.svelte';
    import ErrorMessage from './ErrorMessage.svelte';

    export let error;
    export let header;

    let show_modal = true;

    const dispatch = createEventDispatcher();

    function close() {
        error_stack.set(null);
        show_modal = false;
        dispatch("close");
    }
</script>

<style>
    h1 {
        color: var(--cancel-text-color, red);
        text-align: center;
    }
</style>

{#if show_modal}
    <Modal on:close={close} use_submission={false}>
        <h1>{header}</h1>
        <ErrorMessage error={error} />
    </Modal>
{/if}