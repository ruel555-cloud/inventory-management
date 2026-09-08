<template>
  <div class="app" :class="{ 'is-collapsed': collapsed }">
    <aside class="sidebar">
      <div class="sidebar-top">
        <div v-if="!collapsed" class="brand">
          <h1>{{ t('nav.companyName') }}</h1>
          <span class="brand-sub">{{ t('nav.subtitle') }}</span>
        </div>
        <button
          v-if="!forcedNarrow"
          class="rail-toggle"
          :aria-label="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
          :title="collapsed ? t('nav.expandSidebar') : t('nav.collapseSidebar')"
          :aria-expanded="!collapsed"
          @click="toggleSidebar"
        >
          <svg viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.5"
               stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="2.5" y="3" width="13" height="12" rx="1.5"/>
            <path d="M7 3v12"/>
          </svg>
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link
          to="/"
          :class="{ active: $route.path === '/' }"
          :title="collapsed ? t('nav.overview') : null"
          :aria-label="t('nav.overview')"
        >
          <svg class="nav-icon" viewBox="0 0 18 18" fill="none" stroke="currentColor"
               stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="2.25" y="2.25" width="5.5" height="5.5" rx="1"/><rect x="10.25" y="2.25" width="5.5" height="5.5" rx="1"/><rect x="2.25" y="10.25" width="5.5" height="5.5" rx="1"/><rect x="10.25" y="10.25" width="5.5" height="5.5" rx="1"/>
          </svg>
          <span class="nav-label">{{ t('nav.overview') }}</span>
        </router-link>
        <router-link
          to="/inventory"
          :class="{ active: $route.path === '/inventory' }"
          :title="collapsed ? t('nav.inventory') : null"
          :aria-label="t('nav.inventory')"
        >
          <svg class="nav-icon" viewBox="0 0 18 18" fill="none" stroke="currentColor"
               stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M2.5 5.5 9 2.5l6.5 3v7L9 15.5l-6.5-3z"/><path d="M2.5 5.5 9 8.5l6.5-3M9 8.5v7"/>
          </svg>
          <span class="nav-label">{{ t('nav.inventory') }}</span>
        </router-link>
        <router-link
          to="/orders"
          :class="{ active: $route.path === '/orders' }"
          :title="collapsed ? t('nav.orders') : null"
          :aria-label="t('nav.orders')"
        >
          <svg class="nav-icon" viewBox="0 0 18 18" fill="none" stroke="currentColor"
               stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <rect x="3.5" y="2.5" width="11" height="13" rx="1.5"/><path d="M6.5 6.5h5M6.5 9h5M6.5 11.5h3"/>
          </svg>
          <span class="nav-label">{{ t('nav.orders') }}</span>
        </router-link>
        <router-link
          to="/spending"
          :class="{ active: $route.path === '/spending' }"
          :title="collapsed ? t('nav.finance') : null"
          :aria-label="t('nav.finance')"
        >
          <svg class="nav-icon" viewBox="0 0 18 18" fill="none" stroke="currentColor"
               stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M2.5 4.5h13v9h-13z" rx="1"/><circle cx="9" cy="9" r="2"/>
          </svg>
          <span class="nav-label">{{ t('nav.finance') }}</span>
        </router-link>
        <router-link
          to="/demand"
          :class="{ active: $route.path === '/demand' }"
          :title="collapsed ? t('nav.demandForecast') : null"
          :aria-label="t('nav.demandForecast')"
        >
          <svg class="nav-icon" viewBox="0 0 18 18" fill="none" stroke="currentColor"
               stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M2.5 12.5 6.5 8l3 2.5 5-6"/><path d="M11.5 4.5h3v3"/>
          </svg>
          <span class="nav-label">{{ t('nav.demandForecast') }}</span>
        </router-link>
        <router-link
          to="/restocking"
          :class="{ active: $route.path === '/restocking' }"
          :title="collapsed ? t('nav.restocking') : null"
          :aria-label="t('nav.restocking')"
        >
          <svg class="nav-icon" viewBox="0 0 18 18" fill="none" stroke="currentColor"
               stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M2.5 5.5 9 2.5l6.5 3v7L9 15.5l-6.5-3z"/><path d="M9 7v4M7 9h4"/>
          </svg>
          <span class="nav-label">{{ t('nav.restocking') }}</span>
        </router-link>
        <router-link
          to="/reports"
          :class="{ active: $route.path === '/reports' }"
          :title="collapsed ? 'Reports' : null"
          :aria-label="'Reports'"
        >
          <svg class="nav-icon" viewBox="0 0 18 18" fill="none" stroke="currentColor"
               stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M3 15.5h12"/><path d="M5.5 15.5V9M9 15.5V4.5M12.5 15.5v-4"/>
          </svg>
          <span class="nav-label">{{ 'Reports' }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <LanguageSwitcher />
        <ProfileMenu
          @show-profile-details="showProfileDetails = true"
          @show-tasks="showTasks = true"
        />
      </div>
    </aside>

    <div class="content">
      <FilterBar />
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <ProfileDetailsModal
      :is-open="showProfileDetails"
      @close="showProfileDetails = false"
    />

    <TasksModal
      :is-open="showTasks"
      :tasks="tasks"
      @close="showTasks = false"
      @add-task="addTask"
      @delete-task="deleteTask"
      @toggle-task="toggleTask"
    />
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { api } from './api'
import { useAuth } from './composables/useAuth'
import { useI18n } from './composables/useI18n'
import FilterBar from './components/FilterBar.vue'
import ProfileMenu from './components/ProfileMenu.vue'
import ProfileDetailsModal from './components/ProfileDetailsModal.vue'
import TasksModal from './components/TasksModal.vue'
import LanguageSwitcher from './components/LanguageSwitcher.vue'

export default {
  name: 'App',
  components: {
    FilterBar,
    ProfileMenu,
    ProfileDetailsModal,
    TasksModal,
    LanguageSwitcher
  },
  setup() {
    const { currentUser } = useAuth()
    const { t } = useI18n()
    const showProfileDetails = ref(false)
    const showTasks = ref(false)
    const apiTasks = ref([])

    // Sidebar collapse. The user's manual choice is remembered, but below the
    // breakpoint the rail is forced to icons regardless -- there is no room for
    // labels, so honouring a stored "expanded" there would clip the content.
    const userCollapsed = ref(localStorage.getItem('sidebar-collapsed') === 'true')
    const forcedNarrow = ref(false)
    const collapsed = computed(() => userCollapsed.value || forcedNarrow.value)

    const toggleSidebar = () => {
      userCollapsed.value = !userCollapsed.value
      localStorage.setItem('sidebar-collapsed', String(userCollapsed.value))
    }

    const narrowQuery = window.matchMedia('(max-width: 1100px)')
    const applyNarrow = (e) => { forcedNarrow.value = e.matches }
    applyNarrow(narrowQuery)
    narrowQuery.addEventListener('change', applyNarrow)
    onUnmounted(() => narrowQuery.removeEventListener('change', applyNarrow))

    // Merge mock tasks from currentUser with API tasks
    const tasks = computed(() => {
      return [...currentUser.value.tasks, ...apiTasks.value]
    })

    const loadTasks = async () => {
      try {
        apiTasks.value = await api.getTasks()
      } catch (err) {
        console.error('Failed to load tasks:', err)
      }
    }

    const addTask = async (taskData) => {
      try {
        const newTask = await api.createTask(taskData)
        // Add new task to the beginning of the array
        apiTasks.value.unshift(newTask)
      } catch (err) {
        console.error('Failed to add task:', err)
      }
    }

    const deleteTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const isMockTask = currentUser.value.tasks.some(t => t.id === taskId)

        if (isMockTask) {
          // Remove from mock tasks
          const index = currentUser.value.tasks.findIndex(t => t.id === taskId)
          if (index !== -1) {
            currentUser.value.tasks.splice(index, 1)
          }
        } else {
          // Remove from API tasks
          await api.deleteTask(taskId)
          apiTasks.value = apiTasks.value.filter(t => t.id !== taskId)
        }
      } catch (err) {
        console.error('Failed to delete task:', err)
      }
    }

    const toggleTask = async (taskId) => {
      try {
        // Check if it's a mock task (from currentUser)
        const mockTask = currentUser.value.tasks.find(t => t.id === taskId)

        if (mockTask) {
          // Toggle mock task status
          mockTask.status = mockTask.status === 'pending' ? 'completed' : 'pending'
        } else {
          // Toggle API task
          const updatedTask = await api.toggleTask(taskId)
          const index = apiTasks.value.findIndex(t => t.id === taskId)
          if (index !== -1) {
            apiTasks.value[index] = updatedTask
          }
        }
      } catch (err) {
        console.error('Failed to toggle task:', err)
      }
    }

    onMounted(loadTasks)

    return {
      t,
      collapsed,
      forcedNarrow,
      toggleSidebar,
      showProfileDetails,
      showTasks,
      tasks,
      addTask,
      deleteTask,
      toggleTask
    }
  }
}
</script>

<style>
/* ---------------------------------------------------------------------------
   Design tokens
   Borders carry the structure here, not shadows: this is an operations console
   read for hours at a time, so contrast is spent on data rather than chrome.
   --------------------------------------------------------------------------- */
:root {
  --page: #f4f6f8;
  --panel: #ffffff;
  --inset: #f8fafc;

  --ink: #0f172a;
  --body: #334155;
  --muted: #64748b;
  --faint: #94a3b8;

  --rule: #e3e8ef;
  --rule-strong: #cbd5e1;

  --accent: #2563eb;
  --accent-hover: #1d4ed8;
  --accent-tint: #eff6ff;
  --accent-ring: rgba(37, 99, 235, 0.14);

  --success: #059669;  --success-tint: #d1fae5;  --success-ink: #065f46;
  --warning: #b45309;  --warning-tint: #fef3c7;  --warning-ink: #92400e;
  --danger:  #dc2626;  --danger-tint:  #fee2e2;  --danger-ink:  #991b1b;
  --info:    #2563eb;  --info-tint:    #dbeafe;  --info-ink:    #1e40af;
  --neutral-tint: #e0e7ff; --neutral-ink: #3730a3;

  /* 4px scale */
  --s1: 0.25rem; --s2: 0.5rem;  --s3: 0.75rem; --s4: 1rem;
  --s5: 1.25rem; --s6: 1.5rem;  --s8: 2rem;    --s10: 2.5rem;

  /* Radius varies with hierarchy: page-level panels read as surfaces,
     controls nested inside them read as parts. One radius everywhere is
     what makes a card kit look stamped out. */
  --r-panel: 12px;
  --r-control: 6px;
  --r-pill: 9999px;

  --rail: 232px;
  --rail-collapsed: 64px;
  --content-max: 1440px;
  --t: 140ms ease;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background: var(--page);
  color: var(--body);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Every interactive element gets the same ring, and only on keyboard focus. */
:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  * { transition: none !important; animation: none !important; }
}

/* --- Shell ---------------------------------------------------------------- */

.app {
  display: grid;
  grid-template-columns: var(--rail) 1fr;
  min-height: 100vh;
  /* User-triggered, so the width change is worth animating -- it shows what
     changed. Suppressed by the reduced-motion rule above. */
  transition: grid-template-columns var(--t);
}

.app.is-collapsed {
  grid-template-columns: var(--rail-collapsed) 1fr;
}

.sidebar {
  background: var(--panel);
  border-right: 1px solid var(--rule);
  padding: var(--s6) var(--s3);
  display: flex;
  flex-direction: column;
  gap: var(--s6);
  position: sticky;
  top: 0;
  height: 100vh;
  /* visible, not auto: the footer menus escape the rail's width and would be
     clipped by a scroll container. The nav list scrolls on its own instead. */
  overflow: visible;
}

.sidebar-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--s2);
}

.is-collapsed .sidebar-top { justify-content: center; }

.rail-toggle {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--r-control);
  color: var(--faint);
  cursor: pointer;
  transition: color var(--t), background var(--t), border-color var(--t);
}

.rail-toggle:hover {
  color: var(--ink);
  background: var(--inset);
  border-color: var(--rule);
}

.rail-toggle svg { width: 16px; height: 16px; }

.brand {
  min-width: 0;
  padding: 0 var(--s1);
  display: flex;
  flex-direction: column;
  gap: var(--s1);
}

.brand h1 {
  font-size: 1.0625rem;
  font-weight: 650;
  color: var(--ink);
  letter-spacing: -0.02em;
  line-height: 1.3;
}

.brand-sub {
  font-size: 0.75rem;
  color: var(--faint);
  font-weight: 400;
  line-height: 1.4;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-height: 0;
  overflow-y: auto;
}

/* The active marker is a solid rule on the leading edge -- a physical
   "you are here" tab rather than a colour swap alone, which stays legible
   for anyone who cannot separate the blue from the grey. */
.sidebar-nav a {
  position: relative;
  display: flex;
  align-items: center;
  gap: var(--s3);
  min-height: 36px;
  padding: 0 var(--s3);
  border-radius: var(--r-control);
  color: var(--muted);
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: color var(--t), background var(--t);
}

.sidebar-nav a:hover {
  color: var(--ink);
  background: var(--inset);
}

.sidebar-nav a.active {
  color: var(--accent);
  background: var(--accent-tint);
  font-weight: 600;
}

.sidebar-nav a.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 8px;
  bottom: 8px;
  width: 3px;
  border-radius: var(--r-pill);
  background: var(--accent);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
}

.nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Icons-only rail. The label leaves the DOM, so each link carries an
   aria-label and a title -- otherwise the link would be unnamed for screen
   readers and unidentifiable on hover. */
.is-collapsed .sidebar-nav a {
  justify-content: center;
  padding: 0;
  gap: 0;
}

.is-collapsed .nav-label { display: none; }

.is-collapsed .sidebar-nav a.active::before { left: -4px; }

.is-collapsed .sidebar { padding-left: var(--s2); padding-right: var(--s2); }

.app.is-collapsed .sidebar-footer { align-items: center; }

.app.is-collapsed .profile-name,
.app.is-collapsed .language-label,
.app.is-collapsed .chevron {
  display: none;
}

.app.is-collapsed .profile-button,
.app.is-collapsed .language-button {
  justify-content: center;
  gap: 0;
  padding: var(--s2);
  width: 100%;
}

.sidebar-footer {
  margin-top: auto;
  padding-top: var(--s4);
  border-top: 1px solid var(--rule);
  display: flex;
  flex-direction: column;
  gap: var(--s2);
}

.content {
  display: flex;
  flex-direction: column;
  /* Grid columns default to min-width:auto, so one wide table would push the
     whole layout sideways without this. */
  min-width: 0;
}

.main-content {
  flex: 1;
  width: 100%;
  max-width: var(--content-max);
  padding: var(--s6) var(--s8);
}

/* --- Page header ---------------------------------------------------------- */

.page-header {
  margin-bottom: var(--s6);
}

.page-header h2 {
  font-size: 1.5rem;
  font-weight: 650;
  color: var(--ink);
  margin-bottom: var(--s1);
  letter-spacing: -0.02em;
}

.page-header p {
  color: var(--muted);
  font-size: 0.875rem;
}

/* --- Stats ---------------------------------------------------------------- */

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: var(--s4);
  margin-bottom: var(--s6);
}

.stat-card {
  background: var(--panel);
  padding: var(--s5);
  border-radius: var(--r-panel);
  border: 1px solid var(--rule);
}

.stat-label {
  color: var(--muted);
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: var(--s2);
}

/* Tabular figures so digits line up column to column. In a stock and money
   app, ragged numerals are the actual legibility failure. */
.stat-value {
  font-size: 1.75rem;
  font-weight: 650;
  color: var(--ink);
  letter-spacing: -0.02em;
  font-variant-numeric: tabular-nums;
}

.stat-card.warning .stat-value { color: var(--warning); }
.stat-card.success .stat-value { color: var(--success); }
.stat-card.danger  .stat-value { color: var(--danger); }
.stat-card.info    .stat-value { color: var(--info); }

/* --- Cards ---------------------------------------------------------------- */

.card {
  background: var(--panel);
  border-radius: var(--r-panel);
  padding: var(--s5);
  border: 1px solid var(--rule);
  margin-bottom: var(--s5);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--s4);
  margin-bottom: var(--s4);
  padding-bottom: var(--s3);
  border-bottom: 1px solid var(--rule);
}

.card-title {
  font-size: 1rem;
  font-weight: 650;
  color: var(--ink);
  letter-spacing: -0.01em;
}

/* --- Tables --------------------------------------------------------------- */

.table-container { overflow-x: auto; }

table {
  width: 100%;
  border-collapse: collapse;
  font-variant-numeric: tabular-nums;
}

thead {
  background: var(--inset);
  border-top: 1px solid var(--rule);
  border-bottom: 1px solid var(--rule);
}

th {
  text-align: left;
  padding: var(--s2) var(--s3);
  font-weight: 600;
  color: var(--muted);
  font-size: 0.8125rem;
  white-space: nowrap;
}

td {
  padding: var(--s3);
  border-top: 1px solid var(--rule);
  color: var(--body);
  font-size: 0.875rem;
}

tbody tr { transition: background-color var(--t); }
tbody tr:hover { background: var(--inset); }

/* --- Badges --------------------------------------------------------------- */

.badge {
  display: inline-block;
  padding: 2px var(--s2);
  border-radius: var(--r-pill);
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1.5;
}

.badge.success,
.badge.increasing { background: var(--success-tint); color: var(--success-ink); }

.badge.warning,
.badge.medium     { background: var(--warning-tint); color: var(--warning-ink); }

.badge.danger,
.badge.decreasing,
.badge.high       { background: var(--danger-tint); color: var(--danger-ink); }

.badge.info,
.badge.low        { background: var(--info-tint); color: var(--info-ink); }

.badge.stable     { background: var(--neutral-tint); color: var(--neutral-ink); }

/* --- States --------------------------------------------------------------- */

.loading {
  text-align: center;
  padding: var(--s10);
  color: var(--muted);
  font-size: 0.875rem;
}

.error {
  background: var(--danger-tint);
  border: 1px solid var(--danger-tint);
  border-left: 3px solid var(--danger);
  color: var(--danger-ink);
  padding: var(--s3) var(--s4);
  border-radius: var(--r-control);
  margin: var(--s4) 0;
  font-size: 0.875rem;
}

/* --- Narrow screens ------------------------------------------------------- */

@media (max-width: 640px) {
  .app,
  .app.is-collapsed { grid-template-columns: 1fr; }

  .sidebar {
    position: static;
    height: auto;
    border-right: none;
    border-bottom: 1px solid var(--rule);
    flex-direction: row;
    align-items: center;
    gap: var(--s3);
    padding: var(--s2) var(--s3);
  }

  .sidebar-top { display: none; }

  .sidebar-nav {
    flex-direction: row;
    flex-wrap: nowrap;
    overflow-x: auto;
    flex: 1;
    gap: var(--s1);
  }

  .app.is-collapsed .sidebar-nav a.active::before { left: 0; top: auto; bottom: 0; right: 0; width: auto; height: 2px; }

  .sidebar-footer {
    margin-top: 0;
    padding-top: 0;
    border-top: none;
    flex-direction: row;
    flex-shrink: 0;
  }

  .filters-container { padding: 0 var(--s4); }
  .main-content { padding: var(--s4); }
}

</style>
