<script>
    import { setContext } from 'svelte';
    import { flip } from 'svelte/animate';

    export let items;
    export let columnSizes;
    export let height = "100%";

    setContext('sizes', columnSizes);
</script>

<style>
    .table-container {
        width: 100%;
        display: flex;
        flex-direction: column;
        background: var(--background-color, white);
    }

    .row {
        width: 100%;
        flex-direction: row;
    }

    .items-container {
        width: 100%;
        height: var(--height);
        flex-direction: column;
        overflow-y: auto;
    }
</style>

<div class="table-container">
    <span class="row">
        <slot name="header"></slot>
    </span>
    <span class="items-container" style="--height: {height};">
        <!-- {#each items as item, index (item.name)} -->
        {#each items as item, index}
            <!-- <div animate:flip> -->
                <slot name="item" {item} {index}></slot>
            <!-- </div> -->
        {/each}
    </span>
    <span class="row">
        <slot name="footer"></slot>
    </span>
</div>