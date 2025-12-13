<script>
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	dayjs.extend(relativeTime);

	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { WEBUI_NAME, config, user, showSidebar, knowledge } from '$lib/stores';
	import { WEBUI_BASE_URL } from '$lib/constants';

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import Badge from '$lib/components/common/Badge.svelte';
	import UsersSolid from '$lib/components/icons/UsersSolid.svelte';
	import ChevronRight from '$lib/components/icons/ChevronRight.svelte';
	import EllipsisHorizontal from '$lib/components/icons/EllipsisHorizontal.svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import User from '$lib/components/icons/User.svelte';
	import UserCircleSolid from '$lib/components/icons/UserCircleSolid.svelte';
	import EditGroupModal from './Groups/EditGroupModal.svelte';
	import Pencil from '$lib/components/icons/Pencil.svelte';
	import GroupItem from './Groups/GroupItem.svelte';
	import { createNewGroup, getGroups } from '$lib/apis/groups';
	import {
		getUserDefaultPermissions,
		getAllUsers,
		updateUserDefaultPermissions
	} from '$lib/apis/users';
	import SpinnerFull from '$lib/components/common/SpinnerFull.svelte';

	const i18n = getContext('i18n');

	let loaded = false;

	let users = [];
	let total = 0;

	let groups = [];
	let filteredGroups;

	$: filteredGroups = groups.filter((user) => {
		if (search === '') {
			return true;
		} else {
			let name = user.name.toLowerCase();
			const query = search.toLowerCase();
			return name.includes(query);
		}
	});

	let search = '';
	let defaultPermissions = {};

	let showAddGroupModal = false;
	let showDefaultPermissionsModal = false;

	const setGroups = async () => {
		groups = await getGroups(localStorage.token);
	};

	const addGroupHandler = async (group) => {
		const res = await createNewGroup(localStorage.token, group).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Group created successfully'));
			groups = await getGroups(localStorage.token);
		}
	};

	const updateDefaultPermissionsHandler = async (group) => {
		console.debug(group.permissions);

		const res = await updateUserDefaultPermissions(localStorage.token, group.permissions).catch(
			(error) => {
				toast.error(`${error}`);
				return null;
			}
		);

		if (res) {
			toast.success($i18n.t('Default permissions updated successfully'));
			defaultPermissions = await getUserDefaultPermissions(localStorage.token);
		}
	};

	onMount(async () => {
		if ($user?.role !== 'admin') {
			await goto('/');
			return;
		}

		const res = await getAllUsers(localStorage.token).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			users = res.users;
			total = res.total;
		}

		defaultPermissions = await getUserDefaultPermissions(localStorage.token);
		await setGroups();
		loaded = true;
	});
</script>

{#if loaded}
	<EditGroupModal
		bind:show={showAddGroupModal}
		edit={false}
		permissions={defaultPermissions}
		onSubmit={addGroupHandler}
	/>

	<div class="mb-6 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
		<div class="flex items-center gap-3">
			<h2 class="text-2xl font-semibold text-gray-900 dark:text-white">{$i18n.t('Groups')}</h2>
			<span class="text-2xl font-semibold text-gray-400 dark:text-gray-500">({groups.length})</span>
		</div>

		<div class="flex gap-3 w-full md:w-auto">
			<div class="relative flex-1 md:w-64">
				<div class="absolute inset-y-0 left-3 flex items-center pointer-events-none">
					<Search className="size-4 text-gray-400" />
				</div>
				<input
					class="w-full pl-10 pr-4 py-2 text-sm rounded-lg bg-white dark:bg-gray-850 border border-gray-300 dark:border-gray-700 text-gray-900 dark:text-white placeholder-gray-400 focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-600 focus:border-transparent outline-none transition"
					bind:value={search}
					placeholder={$i18n.t('Search groups...')}
				/>
			</div>

			<button
				class="px-4 py-2 text-sm font-medium bg-green-600 hover:bg-green-700 text-white transition rounded-lg flex items-center gap-2 whitespace-nowrap"
				on:click={() => {
					showAddGroupModal = !showAddGroupModal;
				}}
			>
				<Plus className="size-4" />
				{$i18n.t('Add Group')}
			</button>
		</div>
	</div>

	<div>
		{#if filteredGroups.length === 0}
			<div class="flex flex-col items-center justify-center py-16">
				<div class="text-gray-400 dark:text-gray-600 mb-4">
					<UsersSolid className="size-16" />
				</div>
				<div class="text-xl font-semibold text-gray-900 dark:text-white mb-2">
					{$i18n.t('Organize your users')}
				</div>
				<div class="text-sm text-gray-500 dark:text-gray-400 mb-6">
					{$i18n.t('Use groups to group your users and assign permissions.')}
				</div>
				<button
					class="px-6 py-2.5 text-sm font-medium bg-green-600 hover:bg-green-700 text-white transition rounded-lg flex items-center gap-2"
					aria-label={$i18n.t('Create Group')}
					on:click={() => {
						showAddGroupModal = true;
					}}
				>
					<Plus className="size-4" />
					{$i18n.t('Create Group')}
				</button>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-4">
				{#each filteredGroups as group}
					<GroupItem {group} {users} {setGroups} {defaultPermissions} />
				{/each}
			</div>
		{/if}
	</div>

	<div class="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
		<EditGroupModal
			bind:show={showDefaultPermissionsModal}
			tabs={['permissions']}
			bind:permissions={defaultPermissions}
			custom={false}
			onSubmit={updateDefaultPermissionsHandler}
		/>

		<button
			class="flex items-center justify-between w-full p-4 rounded-lg bg-gray-50 dark:bg-gray-900/50 hover:bg-gray-100 dark:hover:bg-gray-900 border border-gray-200 dark:border-gray-700 transition"
			on:click={() => {
				showDefaultPermissionsModal = true;
			}}
		>
			<div class="flex items-center gap-3">
				<div class="p-2 bg-gray-200 dark:bg-gray-800 rounded-lg">
					<UsersSolid className="size-5 text-gray-600 dark:text-gray-400" />
				</div>
				<div class="text-left">
					<div class="text-sm font-medium text-gray-900 dark:text-white">
						{$i18n.t('Default Permissions')}
					</div>
					<div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
						{$i18n.t('Applies to all users with the "user" role')}
					</div>
				</div>
			</div>
			<div class="text-gray-400">
				<ChevronRight className="size-5" strokeWidth="2" />
			</div>
		</button>
	</div>

{:else}
	<SpinnerFull />
{/if}
