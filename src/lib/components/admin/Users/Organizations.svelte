<script lang="ts">
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	dayjs.extend(relativeTime);

	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { user } from '$lib/stores';

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import OrganizationItem from './Organizations/OrganizationItem.svelte';
	import EditOrganizationModal from './Organizations/EditOrganizationModal.svelte';
	import OrganizationDetailsPanel from './Organizations/OrganizationDetailsPanel.svelte';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';
	import {
		createNewOrganization,
		getOrganizations,
		updateOrganizationById,
		deleteOrganizationById
	} from '$lib/apis/organizations';
	import { getSubscriptionPlans } from '$lib/apis/subscriptions';

	const i18n = getContext('i18n');

	let loaded = false;

	let plans: any[] = [];
	let organizations: any[] = [];
	let filteredOrganizations;

	$: filteredOrganizations = organizations.filter((org) => {
		if (search === '') {
			return true;
		} else {
			let name = org.org_name.toLowerCase();
			let code = org.org_code.toLowerCase();
			const query = search.toLowerCase();
			return name.includes(query) || code.includes(query);
		}
	});

	let search = '';
	let showAddOrganizationModal = false;
	let showEditOrganizationModal = false;
	let selectedOrganization: any = null;
	let showDetailsPanel = false;
	let showDeleteConfirm = false;
	let organizationToDelete: any = null;

	const setOrganizations = async () => {
		organizations = await getOrganizations(localStorage.token);
	};

	const addOrganizationHandler = async (organization: any) => {
		const res = await createNewOrganization(localStorage.token, organization).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Organization created successfully'));
			await setOrganizations();
		}
	};

	const updateOrganizationHandler = async (id: string, organization: any) => {
		const res = await updateOrganizationById(localStorage.token, id, organization).catch(
			(error) => {
				toast.error(`${error}`);
				return null;
			}
		);

		if (res) {
			toast.success($i18n.t('Organization updated successfully'));
			await setOrganizations();
		}
	};

	const deleteOrganizationHandler = async (id: string) => {
		const res = await deleteOrganizationById(localStorage.token, id).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (res) {
			toast.success($i18n.t('Organization deleted successfully'));
			await setOrganizations();
		}
	};

	onMount(async () => {
		if ($user?.role !== 'admin') {
			await goto('/');
			return;
		}

		const resPlans = await getSubscriptionPlans(localStorage.token).catch((error) => {
			toast.error(`${error}`);
			return null;
		});

		if (resPlans) {
			plans = resPlans;
		}

		await setOrganizations();
		loaded = true;
	});
</script>

{#if loaded}
	<EditOrganizationModal
		bind:show={showAddOrganizationModal}
		edit={false}
		{plans}
		onSubmit={addOrganizationHandler}
	/>

	{#if selectedOrganization}
		<EditOrganizationModal
			bind:show={showEditOrganizationModal}
			edit={true}
			organization={selectedOrganization}
			{plans}
			onSubmit={(data) => updateOrganizationHandler(selectedOrganization.id, data)}
		/>
		
		<OrganizationDetailsPanel
			bind:show={showDetailsPanel}
			organization={selectedOrganization}
			{plans}
			onEdit={() => {
				showDetailsPanel = false;
				showEditOrganizationModal = true;
			}}
			onDelete={() => {
				deleteOrganizationHandler(selectedOrganization.id);
				showDetailsPanel = false;
				selectedOrganization = null;
			}}
		/>
	{/if}

	<div class="flex flex-col h-full">
		<!-- Header -->
		<div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
			<h1 class="text-xl sm:text-2xl font-semibold text-gray-900 dark:text-gray-100">
				{$i18n.t('Organization Management')}
			</h1>
			<button
				class="w-full sm:w-auto flex items-center justify-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition font-medium text-sm"
				on:click={() => {
					showAddOrganizationModal = true;
				}}
			>
				<Plus className="size-4" />
				{$i18n.t('Create Organization')}
			</button>
		</div>

		<!-- Table Container -->
		<div class="bg-white dark:bg-gray-900 rounded-lg border border-gray-200 dark:border-gray-800 overflow-hidden">
			<!-- Table Header with Total Count -->
			<div class="flex items-center justify-between px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-800">
				<div class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
					<svg class="size-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
					</svg>
				</div>
				<div class="text-sm text-gray-500 dark:text-gray-400">
					<span class="font-medium">Total:</span> {organizations.length}
				</div>
			</div>

			<!-- Table -->
			{#if filteredOrganizations.length === 0}
				<div class="flex flex-col items-center justify-center py-12 px-4">
					<div class="text-xl font-medium text-gray-900 dark:text-gray-100">
						{$i18n.t('Manage your organizations')}
					</div>

					<div class="mt-2 text-sm text-gray-500 dark:text-gray-400">
						{$i18n.t('Create organizations to group users and assign subscription plans.')}
					</div>

					<div class="mt-6">
						<button
							class="flex items-center gap-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition font-medium text-sm"
							on:click={() => {
								showAddOrganizationModal = true;
							}}
						>
							<Plus className="size-4" />
							{$i18n.t('Create Organization')}
						</button>
					</div>
				</div>
			{:else}
				<!-- Desktop Table View -->
				<div class="hidden md:block overflow-x-auto">
					<table class="w-full">
						<thead class="bg-gray-50 dark:bg-gray-800/50">
							<tr>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
									{$i18n.t('Name')}
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
									{$i18n.t('Code')}
								</th>
								<th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
									{$i18n.t('Plans')}
								</th>
								<th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
									{$i18n.t('Actions')}
								</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-gray-200 dark:divide-gray-800">
							{#each filteredOrganizations as organization}
								<OrganizationItem
									{organization}
									{plans}
									onView={() => {
										selectedOrganization = organization;
										showDetailsPanel = true;
									}}
									onEdit={() => {
										selectedOrganization = organization;
										showEditOrganizationModal = true;
									}}
									onDelete={() => deleteOrganizationHandler(organization.id)}
									onDuplicate={() => {
										// Copy signup link
										const signupUrl = `${window.location.origin}/auth/org/${organization.org_code}`;
										navigator.clipboard.writeText(signupUrl);
										toast.success($i18n.t('Signup link copied to clipboard!'));
									}}
								/>
							{/each}
						</tbody>
					</table>
				</div>

				<!-- Mobile Card View -->
				<div class="md:hidden divide-y divide-gray-200 dark:divide-gray-800">
					{#each filteredOrganizations as organization}
						<div class="p-4">
							<!-- Organization Header -->
							<div class="flex items-start justify-between mb-3">
								<div class="flex-1 min-w-0">
									<div class="text-base font-semibold text-gray-900 dark:text-gray-100 truncate">
										{organization.org_name}
									</div>
									<div class="text-sm font-mono text-gray-500 dark:text-gray-400 mt-0.5">
										{organization.org_code}
									</div>
								</div>
								{#if organization.users && organization.users.length > 0}
									<div class="ml-2 text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded">
										{organization.users.length}
									</div>
								{/if}
							</div>

							<!-- Plans -->
							<div class="mb-3">
								<div class="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">
									{$i18n.t('Plans')}
								</div>
								<div class="flex flex-wrap gap-1.5">
									{#if organization.plans && organization.plans.length > 0}
										{#each organization.plans as planId}
											{@const plan = plans.find((p) => p.id === planId)}
											{@const planName = plan?.plan_name || planId.replace(/[_-]/g, ' ').split(' ').map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()).join(' ')}
											<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400">
												{planName}
											</span>
										{/each}
									{:else}
										<span class="text-sm text-gray-400 dark:text-gray-500">
											{$i18n.t('No plans')}
										</span>
									{/if}
								</div>
							</div>

							<!-- Actions -->
							<div class="flex items-center gap-2">
								<button
									class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30 transition text-sm font-medium"
									on:click={() => {
										selectedOrganization = organization;
										showDetailsPanel = true;
									}}
								>
									<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
									</svg>
									{$i18n.t('View')}
								</button>
								<button
									class="flex-1 flex items-center justify-center gap-1.5 px-3 py-2 rounded-lg bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 hover:bg-purple-100 dark:hover:bg-purple-900/30 transition text-sm font-medium"
									on:click={() => {
										selectedOrganization = organization;
										showEditOrganizationModal = true;
									}}
								>
									<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
									</svg>
									{$i18n.t('Edit')}
								</button>
								<button
									class="p-2 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900/30 transition"
									on:click={() => {
										organizationToDelete = organization;
										showDeleteConfirm = true;
									}}
								>
									<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
									</svg>
								</button>
								<button
									class="p-2 rounded-lg bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/30 transition"
									on:click={() => {
										const signupUrl = `${window.location.origin}/auth/org/${organization.org_code}`;
										navigator.clipboard.writeText(signupUrl);
										toast.success($i18n.t('Signup link copied to clipboard!'));
									}}
								>
									<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
										<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
									</svg>
								</button>
							</div>
						</div>
					{/each}
				</div>
			{/if}
		</div>
	</div>

	<ConfirmDialog
		bind:show={showDeleteConfirm}
		title={$i18n.t('Confirm Deletion')}
		confirmLabel={$i18n.t('Delete')}
		onConfirm={() => {
			if (organizationToDelete) {
				deleteOrganizationHandler(organizationToDelete.id);
				organizationToDelete = null;
			}
		}}
	>
		<div class="text-sm text-gray-500 dark:text-gray-400">
			{$i18n.t('Are you sure you want to delete the organization')}
			<span class="font-bold text-gray-900 dark:text-gray-100">{organizationToDelete?.org_name}</span>?
			<br /><br />
			{$i18n.t('This action cannot be undone.')}
		</div>
	</ConfirmDialog>
{/if}
