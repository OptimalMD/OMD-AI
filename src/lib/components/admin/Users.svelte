<script>
	import { getContext, tick, onMount } from 'svelte';
	import { toast } from 'svelte-sonner';

	import { goto } from '$app/navigation';
	import { user } from '$lib/stores';
	import { page } from '$app/stores';

	import UserList from './Users/UserList.svelte';
	import Groups from './Users/Groups.svelte';
	import Plans from './Users/Plans.svelte';
	import Organizations from './Users/Organizations.svelte';

	const i18n = getContext('i18n');

	let selectedTab;
	$: {
		const pathParts = $page.url.pathname.split('/');
		const tabFromPath = pathParts[pathParts.length - 1];
		selectedTab = ['overview', 'groups', 'plans', 'organizations'].includes(tabFromPath) ? tabFromPath : 'overview';
	}

	$: if (selectedTab) {
		// scroll to selectedTab
		scrollToTab(selectedTab);
	}

	const scrollToTab = (tabId) => {
		const tabElement = document.getElementById(tabId);
		if (tabElement) {
			tabElement.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
		}
	};

	let loaded = false;

	onMount(async () => {
		if ($user?.role !== 'admin') {
			await goto('/');
		}

		loaded = true;

		const containerElement = document.getElementById('users-tabs-container');

		if (containerElement) {
			containerElement.addEventListener('wheel', function (event) {
				if (event.deltaY !== 0) {
					// Adjust horizontal scroll position based on vertical scroll
					containerElement.scrollLeft += event.deltaY;
				}
			});
		}

		// Scroll to the selected tab on mount
		scrollToTab(selectedTab);
	});
</script>

<div class="flex flex-col lg:flex-row w-full h-full pb-2 lg:space-x-6">
	<div
		id="users-tabs-container"
		class="mx-4 lg:ml-4 lg:mr-4 mt-4 lg:mt-0 mb-4 flex flex-row overflow-x-auto gap-2 max-w-full lg:flex-col lg:flex-none lg:w-52 text-sm font-medium scrollbar-none bg-gray-50 dark:bg-gray-900 p-2 rounded-lg"
	>
		<button
			id="overview"
			class="px-4 py-2.5 min-w-fit rounded-lg lg:w-full flex items-center gap-3 text-left transition {selectedTab === 'overview'
				? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-medium'
				: 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'}"
			on:click={() => {
				goto('/admin/users/overview');
			}}
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 16 16"
				fill="currentColor"
				class="size-4 flex-shrink-0"
			>
				<path
					d="M8.5 4.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0ZM10.9 12.006c.11.542-.348.994-.9.994H2c-.553 0-1.01-.452-.902-.994a5.002 5.002 0 0 1 9.803 0ZM14.002 12h-1.59a2.556 2.556 0 0 0-.04-.29 6.476 6.476 0 0 0-1.167-2.603 3.002 3.002 0 0 1 3.633 1.911c.18.522-.283.982-.836.982ZM12 8a2 2 0 1 0 0-4 2 2 0 0 0 0 4Z"
				/>
			</svg>
			<span>{$i18n.t('Overview')}</span>
		</button>

		<button
			id="groups"
			class="px-4 py-2.5 min-w-fit rounded-lg lg:w-full flex items-center gap-3 text-left transition {selectedTab === 'groups'
				? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-medium'
				: 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'}"
			on:click={() => {
				goto('/admin/users/groups');
			}}
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 16 16"
				fill="currentColor"
				class="size-4 flex-shrink-0"
			>
				<path
					d="M8 8a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5ZM3.156 11.763c.16-.629.44-1.21.813-1.72a2.5 2.5 0 0 0-2.725 1.377c-.136.287.102.58.418.58h1.449c.01-.077.025-.156.045-.237ZM12.847 11.763c.02.08.036.16.046.237h1.446c.316 0 .554-.293.417-.579a2.5 2.5 0 0 0-2.722-1.378c.374.51.653 1.09.813 1.72ZM14 7.5a1.5 1.5 0 1 1-3 0 1.5 1.5 0 0 1 3 0ZM3.5 9a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3ZM5 13c-.552 0-1.013-.455-.876-.99a4.002 4.002 0 0 1 7.753 0c.136.535-.324.99-.877.99H5Z"
				/>
			</svg>
			<span>{$i18n.t('Groups')}</span>
		</button>

		<button
			id="plans"
			class="px-4 py-2.5 min-w-fit rounded-lg lg:w-full flex items-center gap-3 text-left transition {selectedTab === 'plans'
				? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-medium'
				: 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'}"
			on:click={() => {
				goto('/admin/users/plans');
			}}
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 16 16"
				fill="currentColor"
				class="size-4 flex-shrink-0"
			>
				<path
					d="M2.5 3A1.5 1.5 0 0 0 1 4.5v.793c.026.009.051.02.076.032L7.674 8.51c.206.1.446.1.652 0l6.598-3.185A.755.755 0 0 1 15 5.293V4.5A1.5 1.5 0 0 0 13.5 3h-11Z"
				/>
				<path
					d="M15 6.954 8.978 9.86a2.25 2.25 0 0 1-1.956 0L1 6.954V11.5A1.5 1.5 0 0 0 2.5 13h11a1.5 1.5 0 0 0 1.5-1.5V6.954Z"
				/>
			</svg>
			<span>{$i18n.t('Plans')}</span>
		</button>

		<button
			id="organizations"
			class="px-4 py-2.5 min-w-fit rounded-lg lg:w-full flex items-center gap-3 text-left transition {selectedTab === 'organizations'
				? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 font-medium'
				: 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'}"
			on:click={() => {
				goto('/admin/users/organizations');
			}}
		>
			<svg
				xmlns="http://www.w3.org/2000/svg"
				viewBox="0 0 16 16"
				fill="currentColor"
				class="size-4 flex-shrink-0"
			>
				<path
					fill-rule="evenodd"
					d="M0 3.5A1.5 1.5 0 0 1 1.5 2h13A1.5 1.5 0 0 1 16 3.5v6A1.5 1.5 0 0 1 14.5 11h-13A1.5 1.5 0 0 1 0 9.5v-6Zm1.5.5a.5.5 0 0 0-.5.5v6a.5.5 0 0 0 .5.5h13a.5.5 0 0 0 .5-.5v-6a.5.5 0 0 0-.5-.5h-13Z"
					clip-rule="evenodd"
				/>
				<path
					d="M2 5.5a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 .5.5V7a.5.5 0 0 1-.5.5h-2A.5.5 0 0 1 2 7V5.5Zm5 0a.5.5 0 0 1 .5-.5h2a.5.5 0 0 1 .5.5V7a.5.5 0 0 1-.5.5h-2A.5.5 0 0 1 7 7V5.5Zm5 0a.5.5 0 0 1 .5-.5h1a.5.5 0 0 1 .5.5V7a.5.5 0 0 1-.5.5h-1a.5.5 0 0 1-.5-.5V5.5ZM3.5 8a.5.5 0 0 0-.5.5V10a.5.5 0 0 0 .5.5h9a.5.5 0 0 0 .5-.5V8.5a.5.5 0 0 0-.5-.5h-9Z"
				/>
			</svg>
			<span>{$i18n.t('Organization')}</span>
		</button>
	</div>

	<div class="flex-1 mt-1 lg:mt-0 px-[16px] lg:pr-[16px] lg:pl-0 overflow-y-scroll">
		{#if selectedTab === 'overview'}
			<UserList />
		{:else if selectedTab === 'groups'}
			<Groups />
		{:else if selectedTab === 'plans'}
			<Plans />
		{:else if selectedTab === 'organizations'}
			<Organizations />
		{/if}
	</div>
</div>
