<script>
  import { OverflowMenu as CcsOverflowMenu } from "carbon-components-svelte";

  /** Persist the open state when click the items */
  export let persistentClickItems = false;

  const handleClose = (event) => {
    // ccs dispatches `close` with a non-null detail only when an item was selected
    if (persistentClickItems && event.detail) {
      event.preventDefault();
    }
  };
</script>

<svelte:component this={CcsOverflowMenu} {...$$restProps} on:close={handleClose}>
  <slot />
</svelte:component>
