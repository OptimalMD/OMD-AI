<script>
	import { WEBUI_BASE_URL } from '$lib/constants';
	import { WEBUI_NAME, config, user, showSidebar } from '$lib/stores';
	import { goto } from '$app/navigation';
	import { onMount, getContext } from 'svelte';

	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	import localizedFormat from 'dayjs/plugin/localizedFormat';
	dayjs.extend(relativeTime);
	dayjs.extend(localizedFormat);

	import { toast } from 'svelte-sonner';

	import { updateUserRole, getUsers, deleteUserById } from '$lib/apis/users';

	import Pagination from '$lib/components/common/Pagination.svelte';
	import ChatBubbles from '$lib/components/icons/ChatBubbles.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';

	import EditUserModal from '$lib/components/admin/Users/UserList/EditUserModal.svelte';
	import UserChatsModal from '$lib/components/admin/Users/UserList/UserChatsModal.svelte';
	import AddUserModal from '$lib/components/admin/Users/UserList/AddUserModal.svelte';

	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import RoleUpdateConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	import Badge from '$lib/components/common/Badge.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import ChevronUp from '$lib/components/icons/ChevronUp.svelte';
	import ChevronDown from '$lib/components/icons/ChevronDown.svelte';
	import About from '$lib/components/chat/Settings/About.svelte';
	import Banner from '$lib/components/common/Banner.svelte';
	import Markdown from '$lib/components/chat/Messages/Markdown.svelte';
	import Spinner from '$lib/components/common/Spinner.svelte';
	import Loader from '$lib/components/common/Loader.svelte';
	import SpinnerFull from '$lib/components/common/SpinnerFull.svelte';

	const i18n = getContext('i18n');

	let page = 1;

	let users = null;
	let total = null;

	let query = '';
	let orderBy = 'created_at'; // default sort key
	let direction = 'desc'; // default sort order

	let selectedUser = null;

	let showDeleteConfirmDialog = false;
	let showAddUserModal = false;

	let showUserChatsModal = false;
	let showEditUserModal = false;

	// Calculate stats
	$: activeUsers24h = users
		? users.filter((u) => {
				const now = Math.floor(Date.now() / 1000);
				return u.last_active_at && now - u.last_active_at < 24 * 60 * 60;
		  }).length
		: 0;

	$: activityRate = total > 0 ? Math.round((activeUsers24h / total) * 100) : 0;

	$: adminCount = users ? users.filter((u) => u.role === 'admin').length : 0;
	$: userCount = users ? users.filter((u) => u.role === 'user').length : 0;
	$: pendingCount = users ? users.filter((u) => u.role === 'pending').length : 0;

	const deleteUserHandler = async (id) => {
		const res = await deleteUserById(localStorage.token, id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		// if the user is deleted and the current page has only one user, go back to the previous page
		if (users.length === 1 && page > 1) {
			page -= 1;
		}

		if (res) {
			getUserList();
		}
	};

	const setSortKey = (key) => {
		if (orderBy === key) {
			direction = direction === 'asc' ? 'desc' : 'asc';
		} else {
			orderBy = key;
			direction = 'asc';
		}
	};

	const getUserList = async () => {
		try {
			const res = await getUsers(localStorage.token, query, orderBy, direction, page).catch(
				(error) => {
					toast.error(`${error}`);
					return null;
				}
			);

			if (res) {
				users = res.users;
				total = res.total;
			}
		} catch (err) {
			console.error(err);
		}
	};

	$: if (page) {
		getUserList();
	}

	$: if (query !== null && orderBy && direction) {
		getUserList();
	}
</script>

<ConfirmDialog
	bind:show={showDeleteConfirmDialog}
	on:confirm={() => {
		deleteUserHandler(selectedUser.id);
	}}
/>

<AddUserModal
	bind:show={showAddUserModal}
	on:save={async () => {
		getUserList();
	}}
/>

<EditUserModal
	bind:show={showEditUserModal}
	{selectedUser}
	sessionUser={$user}
	on:save={async () => {
		getUserList();
	}}
/>

{#if selectedUser}
	<UserChatsModal bind:show={showUserChatsModal} user={selectedUser} />
{/if}

{#if ($config?.license_metadata?.seats ?? null) !== null && total && total > $config?.license_metadata?.seats}
	<div class="mt-4 text-xs">
		<Banner
			className="mx-0"
			banner={{
				type: 'error',
				title: 'License Error',
				content:
					'Exceeded the number of seats in your license. Please contact support to increase the number of seats.'
			}}
		/>
	</div>
{/if}

{#if users === null || total === null}
	<SpinnerFull />
{:else}
	<!-- Header with Title and Add Button -->
	<div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4 sm:mb-6">
		<h1 class="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-white">
			{$i18n.t('User Management')}
		</h1>
		<button
			class="px-3 sm:px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center gap-2 transition-colors text-sm sm:text-base w-full sm:w-auto justify-center"
			on:click={() => {
				showAddUserModal = !showAddUserModal;
			}}
		>
			<Plus className="size-4" />
			{$i18n.t('Add User')}
		</button>
	</div>

	<!-- Stats Cards -->
	<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4 mb-4 sm:mb-6">
		<!-- Total Users Card -->
		<div class="bg-white dark:bg-gray-850 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-gray-200 dark:border-gray-800">
			<div class="flex justify-between items-start">
				<div>
					<div class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1">
						{$i18n.t('Total Users')}
					</div>
					<div class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{total}</div>
				</div>
				<div class="p-2 sm:p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="currentColor"
						class="size-5 sm:size-6 text-blue-600 dark:text-blue-400"
					>
						<path
							d="M4.5 6.375a4.125 4.125 0 118.25 0 4.125 4.125 0 01-8.25 0zM14.25 8.625a3.375 3.375 0 116.75 0 3.375 3.375 0 01-6.75 0zM1.5 19.125a7.125 7.125 0 0114.25 0v.003l-.001.119a.75.75 0 01-.363.63 13.067 13.067 0 01-6.761 1.873c-2.472 0-4.786-.684-6.76-1.873a.75.75 0 01-.364-.63l-.001-.122zM17.25 19.128l-.001.144a2.25 2.25 0 01-.233.96 10.088 10.088 0 005.06-1.01.75.75 0 00.42-.643 4.875 4.875 0 00-6.957-4.611 8.586 8.586 0 011.71 5.157v.003z"
						/>
					</svg>
				</div>
			</div>
		</div>

		<!-- Active Users Card -->
		<div class="bg-white dark:bg-gray-850 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-gray-200 dark:border-gray-800">
			<div class="flex justify-between items-start mb-3">
				<div>
					<div class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1">
						{$i18n.t('Active Users (24h)')}
					</div>
					<div class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{activeUsers24h}</div>
				</div>
				<div class="p-2 sm:p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="currentColor"
						class="size-5 sm:size-6 text-green-600 dark:text-green-400"
					>
						<path
							fill-rule="evenodd"
							d="M12.963 2.286a.75.75 0 00-1.071-.136 9.742 9.742 0 00-3.539 6.177A7.547 7.547 0 016.648 6.61a.75.75 0 00-1.152-.082A9 9 0 1015.68 4.534a7.46 7.46 0 01-2.717-2.248zM15.75 14.25a3.75 3.75 0 11-7.313-1.172c.628.465 1.35.81 2.133 1a5.99 5.99 0 011.925-3.545 3.75 3.75 0 013.255 3.717z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
			</div>
			<div class="flex items-center gap-2">
				<div class="text-xs text-gray-500 dark:text-gray-400">{$i18n.t('Activity Rate')}</div>
				<div class="flex-1 bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
					<div
						class="bg-green-500 h-full transition-all duration-300"
						style="width: {activityRate}%"
					></div>
				</div>
				<div class="text-xs font-medium text-gray-700 dark:text-gray-300">{activityRate}%</div>
			</div>
		</div>

		<!-- User Roles Card -->
		<div class="bg-white dark:bg-gray-850 rounded-lg sm:rounded-xl p-4 sm:p-5 border border-gray-200 dark:border-gray-800">
			<div class="flex justify-between items-start">
				<div>
					<div class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mb-1">
						{$i18n.t('User Roles')}
					</div>
					<div class="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white">{total}</div>
				</div>
				<div class="p-2 sm:p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
					<svg
						xmlns="http://www.w3.org/2000/svg"
						viewBox="0 0 24 24"
						fill="currentColor"
						class="size-5 sm:size-6 text-purple-600 dark:text-purple-400"
					>
						<path
							fill-rule="evenodd"
							d="M12.516 2.17a.75.75 0 00-1.032 0 11.209 11.209 0 01-7.877 3.08.75.75 0 00-.722.515A12.74 12.74 0 002.25 9.75c0 5.942 4.064 10.933 9.563 12.348a.749.749 0 00.374 0c5.499-1.415 9.563-6.406 9.563-12.348 0-1.39-.223-2.73-.635-3.985a.75.75 0 00-.722-.516l-.143.001c-2.996 0-5.717-1.17-7.734-3.08zm3.094 8.016a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z"
							clip-rule="evenodd"
						/>
					</svg>
				</div>
			</div>
			<div class="flex flex-wrap gap-2 mt-3 text-xs">
				<div class="flex items-center gap-1">
					<span class="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-md font-medium"
						>{$i18n.t('Admin')}: {adminCount}</span
					>
				</div>
				<div class="flex items-center gap-1">
					<span class="px-2 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-md font-medium"
						>{$i18n.t('User')}: {userCount}</span
					>
				</div>
				<div class="flex items-center gap-1">
					<span class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md font-medium"
						>{$i18n.t('Pending')}: {pendingCount}</span
					>
				</div>
			</div>
		</div>
	</div>

	<!-- Search Bar and Sort -->
	<div class="mb-4 flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
		<div class="flex-1 relative">
			<div class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					viewBox="0 0 20 20"
					fill="currentColor"
					class="w-4 h-4 sm:w-5 sm:h-5"
				>
					<path
						fill-rule="evenodd"
						d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
						clip-rule="evenodd"
					/>
				</svg>
			</div>
			<input
				class="w-full pl-9 sm:pl-10 pr-4 py-2 sm:py-2.5 bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 rounded-lg text-xs sm:text-sm text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
				bind:value={query}
				placeholder={$i18n.t('Search by name or email...')}
			/>
		</div>
		<div class="flex gap-2 sm:gap-3">
			<div class="relative flex-1 sm:flex-initial">
				<select
					class="w-full px-3 sm:px-4 py-2 sm:py-2.5 bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 rounded-lg text-xs sm:text-sm text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none pr-8"
					bind:value={orderBy}
					on:change={() => (direction = 'desc')}
				>
					<option value="created_at">{$i18n.t('Created')}</option>
					<option value="name">{$i18n.t('Name')}</option>
					<option value="email">{$i18n.t('Email')}</option>
					<option value="last_active_at">{$i18n.t('Last Active')}</option>
				</select>
				<div class="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
					<ChevronDown className="size-3 sm:size-4 text-gray-400" />
				</div>
			</div>
			<button
				class="px-3 sm:px-4 py-2 sm:py-2.5 bg-white dark:bg-gray-850 border border-gray-200 dark:border-gray-800 rounded-lg text-xs sm:text-sm hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
				on:click={() => (direction = direction === 'asc' ? 'desc' : 'asc')}
			>
				{#if direction === 'asc'}
					<ChevronUp className="size-3 sm:size-4" />
				{:else}
					<ChevronDown className="size-3 sm:size-4" />
				{/if}
			</button>
		</div>
	</div>

	<!-- Users Table -->
	<div class="bg-white dark:bg-gray-850 rounded-lg sm:rounded-xl border border-gray-200 dark:border-gray-800 overflow-hidden">
		<div class="overflow-x-auto">
			<table class="w-full min-w-[640px]">
				<thead>
					<tr class="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-800">
						<th class="px-3 sm:px-6 py-2.5 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
							{$i18n.t('User')}
						</th>
						<th class="px-3 sm:px-6 py-2.5 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
							{$i18n.t('Role')}
						</th>
						<th class="px-3 sm:px-6 py-2.5 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider hidden md:table-cell">
							{$i18n.t('Last Active')}
						</th>
						<th class="px-3 sm:px-6 py-2.5 sm:py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider hidden lg:table-cell">
							{$i18n.t('Created')}
						</th>
						<th class="px-3 sm:px-6 py-2.5 sm:py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
							{$i18n.t('Actions')}
						</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-gray-200 dark:divide-gray-800">
					{#if users.length === 0}
						<tr>
							<td colspan="5" class="px-3 sm:px-6 py-12 sm:py-16">
								<div class="flex flex-col items-center justify-center text-center">
									<div class="mb-3 sm:mb-4">
										<svg
											xmlns="http://www.w3.org/2000/svg"
											fill="none"
											viewBox="0 0 24 24"
											stroke-width="1.5"
											stroke="currentColor"
											class="w-12 h-12 sm:w-16 sm:h-16 text-gray-300 dark:text-gray-600"
										>
											<path
												stroke-linecap="round"
												stroke-linejoin="round"
												d="M9 3.75H6.912a2.25 2.25 0 00-2.15 1.588L2.35 13.177a2.25 2.25 0 00-.1.661V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18v-4.162c0-.224-.034-.447-.1-.661L19.24 5.338a2.25 2.25 0 00-2.15-1.588H15M2.25 13.5h3.86a2.25 2.25 0 012.012 1.244l.256.512a2.25 2.25 0 002.013 1.244h3.218a2.25 2.25 0 002.013-1.244l.256-.512a2.25 2.25 0 012.013-1.244h3.859M12 3v8.25m0 0l-3-3m3 3l3-3"
											/>
										</svg>
									</div>
									<h3 class="text-base sm:text-lg font-medium text-gray-900 dark:text-white mb-1">
										{$i18n.t('No users found')}
									</h3>
									<p class="text-xs sm:text-sm text-gray-500 dark:text-gray-400">
										{$i18n.t('Try adjusting your search criteria')}
									</p>
								</div>
							</td>
						</tr>
					{:else}
						{#each users as user}
							<tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
								<!-- User Info -->
								<td class="px-3 sm:px-6 py-3 sm:py-4">
								<div class="flex items-center gap-2 sm:gap-3">
									<img
										class="w-8 h-8 sm:w-10 sm:h-10 rounded-full object-cover flex-shrink-0"
										src={user?.profile_image_url?.startsWith(WEBUI_BASE_URL) ||
										user.profile_image_url.startsWith('https://www.gravatar.com/avatar/') ||
										user.profile_image_url.startsWith('data:')
											? user.profile_image_url
											: `${WEBUI_BASE_URL}/user.png`}
										alt={user.name}
									/>
									<div class="min-w-0">
										<div class="text-xs sm:text-sm font-medium text-gray-900 dark:text-white truncate">
											{user.name}
										</div>
										<div class="text-xs sm:text-sm text-gray-500 dark:text-gray-400 truncate">{user.email}</div>
									</div>
								</div>
							</td>

							<!-- Role -->
							<td class="px-3 sm:px-6 py-3 sm:py-4">
								<button
									on:click={() => {
										selectedUser = user;
										showEditUserModal = !showEditUserModal;
									}}
								>
									{#if user.role === 'admin'}
										<span class="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-md text-xs font-medium">
											{$i18n.t('Admin')}
										</span>
									{:else if user.role === 'user'}
										<span class="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300 rounded-md text-xs font-medium">
											{$i18n.t('User')}
										</span>
									{:else}
										<span class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-md text-xs font-medium">
											{$i18n.t('Pending')}
										</span>
									{/if}
								</button>
							</td>

							<!-- Last Active -->
							<td class="px-3 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm text-gray-600 dark:text-gray-300 hidden md:table-cell">
								{dayjs(user.last_active_at * 1000).fromNow()}
							</td>

							<!-- Created -->
							<td class="px-3 sm:px-6 py-3 sm:py-4 text-xs sm:text-sm text-gray-600 dark:text-gray-300 hidden lg:table-cell">
								{dayjs(user.created_at * 1000).format('LL')}
							</td>

							<!-- Actions -->
							<td class="px-3 sm:px-6 py-3 sm:py-4">
								<div class="flex items-center justify-end gap-1">
									{#if $config.features.enable_admin_chat_access && user.role !== 'admin'}
										<Tooltip content={$i18n.t('Chats')}>
											<button
												class="p-1.5 sm:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors text-blue-600 dark:text-blue-400"
												on:click={async () => {
													showUserChatsModal = !showUserChatsModal;
													selectedUser = user;
												}}
											>
												<ChatBubbles className="size-4 sm:size-5" />
											</button>
										</Tooltip>
									{/if}

									<Tooltip content={$i18n.t('Edit User')}>
										<button
											class="p-1.5 sm:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors text-blue-600 dark:text-blue-400"
											on:click={async () => {
												showEditUserModal = !showEditUserModal;
												selectedUser = user;
											}}
										>
											<svg
												xmlns="http://www.w3.org/2000/svg"
												fill="none"
												viewBox="0 0 24 24"
												stroke-width="1.5"
												stroke="currentColor"
												class="w-4 h-4 sm:w-5 sm:h-5"
											>
												<path
													stroke-linecap="round"
													stroke-linejoin="round"
													d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.13-1.897L16.863 4.487Zm0 0L19.5 7.125"
												/>
											</svg>
										</button>
									</Tooltip>

									{#if user.role !== 'admin'}
										<Tooltip content={$i18n.t('Delete User')}>
											<button
												class="p-1.5 sm:p-2 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors text-red-600 dark:text-red-400"
												on:click={async () => {
													showDeleteConfirmDialog = true;
													selectedUser = user;
												}}
											>
												<svg
													xmlns="http://www.w3.org/2000/svg"
													fill="none"
													viewBox="0 0 24 24"
													stroke-width="1.5"
													stroke="currentColor"
													class="w-4 h-4 sm:w-5 sm:h-5"
												>
													<path
														stroke-linecap="round"
														stroke-linejoin="round"
														d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0"
													/>
												</svg>
											</button>
										</Tooltip>
									{/if}
								</div>
							</td>
						</tr>
					{/each}
					{/if}
				</tbody>
			</table>
		</div>
	</div>

	<!-- Pagination and Info -->
	{#if users.length > 0}
		<div class="mt-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
			<div class="text-xs text-gray-500 dark:text-gray-400 italic">
				{$i18n.t("Click on the user role button to change a user's role.")}
			</div>
			{#if total > 30}
				<Pagination bind:page count={total} perPage={30} />
			{/if}
		</div>
	{/if}
{/if}


<style>
	/* Custom scrollbar */
	:global(.scrollbar-hidden::-webkit-scrollbar) {
		display: none;
	}
	:global(.scrollbar-hidden) {
		-ms-overflow-style: none;
		scrollbar-width: none;
	}
</style>
