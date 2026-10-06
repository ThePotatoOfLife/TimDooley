function createInspectorRouter(options = {}) {
  const emit = typeof options.emit === 'function'
    ? options.emit
    : detail => {
        if (typeof window !== 'undefined') {
          window.dispatchEvent(new CustomEvent('potato-atlas-inspector-change', { detail }));
        }
      };
  let stack = [];

  function captureFocusTarget() {
    if (typeof document === 'undefined') return null;
    const element = document.activeElement;
    if (!element || element === document.body || element === document.documentElement) return null;
    return typeof element.focus === 'function' ? element : null;
  }
  function focusInspectorHeading() {
    if (typeof document === 'undefined') return false;
    const panel = document.getElementById('panel');
    const heading = panel?.querySelector(':scope > h1, :scope > h2, [data-inspector-heading]');
    if (!heading || typeof heading.focus !== 'function') return false;
    if (!heading.hasAttribute('tabindex')) heading.setAttribute('tabindex', '-1');
    queueMicrotask(() => heading.isConnected && heading.focus({preventScroll:false}));
    return true;
  }
  function restoreFocus(target) {
    if (!target || typeof target.focus !== 'function') return false;
    queueMicrotask(() => target.isConnected && target.focus({preventScroll:true}));
    return true;
  }

  function normalizeNode(node = {}) {
    const type = String(node.type || '').trim();
    const id = String(node.id || '').trim();
    const owner = String(node.owner || '').trim();
    if (!type || !id || !owner) throw new TypeError('inspector node requires type, id and owner');
    const parent = node.parent && typeof node.parent === 'object'
      ? { type:String(node.parent.type || '').trim(), id:String(node.parent.id || '').trim() }
      : null;
    return {
      type,
      id,
      owner,
      parent:parent?.type && parent?.id ? parent : null,
      render:typeof node.render === 'function' ? node.render : null,
      restore:typeof node.restore === 'function' ? node.restore : null,
      returnFocus:node.returnFocus || null,
    };
  }

  function publicNode(node) {
    if (!node) return null;
    return { type:node.type, id:node.id, owner:node.owner, parent:node.parent ? { ...node.parent } : null };
  }
  function snapshot(reason = 'change') {
    const detail = { reason, current:publicNode(stack.at(-1)), stack:stack.map(publicNode), depth:stack.length };
    emit(detail);
    return detail;
  }
  function invoke(node) {
    if (!node) return false;
    if (node.render) node.render();
    else if (node.restore) node.restore();
    return Boolean(node.render || node.restore);
  }
  function setBaseline(node) {
    const next = normalizeNode(node);
    const currentBaseline = stack[0];
    const changed = !currentBaseline || currentBaseline.type !== next.type || currentBaseline.id !== next.id || currentBaseline.owner !== next.owner;
    stack = changed ? [next] : [next, ...stack.slice(1)];
    snapshot(changed ? 'baseline' : 'baseline-refresh');
    return true;
  }
  function open(node) {
    const focusTarget = node?.returnFocus || captureFocusTarget();
    const next = normalizeNode({ ...node, returnFocus:focusTarget });
    if (!stack.length) throw new Error('inspector baseline must be set before opening a child node');
    const top = stack.at(-1);
    if (top?.type === next.type && top?.id === next.id && top?.owner === next.owner) {
      stack[stack.length - 1] = next;
      invoke(next);
      focusInspectorHeading();
      snapshot('refresh');
      return true;
    }
    const existingIndex = stack.findIndex(row => row.type === next.type && row.id === next.id && row.owner === next.owner);
    if (existingIndex >= 0) {
      stack = stack.slice(0, existingIndex);
    } else if (next.parent) {
      const parentIndex = stack.map((row, index) => ({ row, index }))
        .filter(({row}) => row.type === next.parent.type && row.id === next.parent.id)
        .at(-1)?.index;
      if (Number.isInteger(parentIndex)) stack = stack.slice(0, parentIndex + 1);
    }
    stack.push(next);
    invoke(next);
    focusInspectorHeading();
    snapshot('open');
    return true;
  }
  function back() {
    if (stack.length <= 1) return false;
    const closed = stack.pop();
    const next = stack.at(-1);
    invoke(next);
    if (!restoreFocus(closed?.returnFocus)) focusInspectorHeading();
    snapshot('back');
    return true;
  }
  function reset(node = null) {
    if (node) {
      const next = normalizeNode(node);
      stack = [next];
      invoke(next);
    } else stack = [];
    snapshot('reset');
    return true;
  }
  function current() { return publicNode(stack.at(-1)); }
  function state() { return { current:current(), stack:stack.map(publicNode), depth:stack.length }; }
  return Object.freeze({ setBaseline, open, back, reset, current, state });
}

if (typeof window !== 'undefined') {
  window.__potatoAtlasInspector = window.__potatoAtlasInspector || createInspectorRouter();
}

export { createInspectorRouter };
