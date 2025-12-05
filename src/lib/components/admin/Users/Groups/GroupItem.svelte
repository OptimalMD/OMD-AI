<script>
	import { toast } from 'svelte-sonner';
	import { onMount, getContext } from 'svelte';
	import { page } from '$app/stores';

	const i18n = getContext('i18n');

	import { deleteGroupById, updateGroupById } from '$lib/apis/groups';

	import Pencil from '$lib/components/icons/Pencil.svelte';
	import User from '$lib/components/icons/User.svelte';
	import UserCircleSolid from '$lib/components/icons/UserCircleSolid.svelte';
	import GroupModal from './EditGroupModal.svelte';

	export let users = [];
	export let group = {
		name: 'Admins',
		user_ids: [1, 2, 3]
	};
	export let defaultPermissions = {};

	export let setGroups = () => {};

	let showEdit = false;

	const updateHandler = async (_group) => {
		const res = await updateGroupById(localStorage.token, group.id, _group).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Group updated successfully'));
			setGroups();
		}
	};

	const deleteHandler = async () => {
		const res = await deleteGroupById(localStorage.token, group.id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Group deleted successfully'));
			setGroups();
		}
	};

	onMount(() => {
		const groupId = $page.url.searchParams.get('id');
		if (groupId && groupId === group.id) {
			showEdit = true;
		}
	});
</script>

<GroupModal
	bind:show={showEdit}
	edit
	{users}
	{group}
	{defaultPermissions}
	onSubmit={updateHandler}
	onDelete={deleteHandler}
/>

<div class="bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-700 rounded-lg p-5 hover:border-gray-300 dark:hover:border-gray-600 transition group">
	<div class="flex items-start justify-between">
		<div class="flex-1 min-w-0">
			<h3 class="text-base font-medium text-gray-900 dark:text-white truncate mb-2">
				{group.name}
			</h3>
			<div class="flex items-center gap-1.5 text-sm text-gray-500 dark:text-gray-400">
				<User className="size-4" />
				<span>{group.user_ids?.length || 0} {$i18n.t('users')}</span>
			</div>
		</div>
		<button
			class="p-2 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition"
			on:click={() => {
				showEdit = true;
			}}
		>
			<Pencil className="size-4" />
		</button>
	</div>
</div>
