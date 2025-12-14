<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { getContext } from 'svelte';
	import Modal from '$lib/components/common/Modal.svelte';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	const i18n = getContext('i18n');

	export let show = false;
	export let organization: any = {};
	export let plans: any[] = [];
	export let onEdit = () => {};
	export let onDelete = () => {};

	let showDeleteConfirm = false;

	$: signupUrl = organization?.org_code 
		? `${window.location.origin}/auth/org/${organization.org_code}` 
		: '';

	const copySignupLink = () => {
		if (signupUrl) {
			navigator.clipboard.writeText(signupUrl);
			toast.success($i18n.t('Registration link copied to clipboard!'));
		}
	};

	const getPlanName = (planId: string) => {
		// First try to find the plan in the plans array
		const plan = plans.find((p: any) => p.id === planId || p.plan_id === planId);
		if (plan) {
			return plan.name || plan.plan_name || formatPlanId(planId);
		}
		// Fallback: format the plan ID nicely
		return formatPlanId(planId);
	};

	const formatPlanId = (planId: string) => {
		// Convert snake_case or kebab-case to Title Case
		return planId
			.replace(/[_-]/g, ' ')
			.split(' ')
			.map((word: string) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
			.join(' ');
	};
</script>

{#if show}
	<Modal bind:show size="lg">
		<div class="p-0">
			<!-- Header with close button -->
			<div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700">
				<h2 class="text-lg font-semibold text-gray-900 dark:text-gray-100">
					{$i18n.t('Organization Details')}
				</h2>
				<div class="flex items-center gap-1">
					<button
						class="p-2 rounded-lg hover:bg-purple-50 dark:hover:bg-purple-900/20 text-purple-600 dark:text-purple-400 transition"
						on:click={onEdit}
						title={$i18n.t('Edit')}
					>
						<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
						</svg>
					</button>
					<button
						class="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 transition"
						on:click={() => {
							showDeleteConfirm = true;
						}}
						title={$i18n.t('Delete')}
					>
						<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
						</svg>
					</button>
					<button
						class="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition"
						on:click={() => show = false}
						title={$i18n.t('Close')}
					>
						<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
							<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
						</svg>
					</button>
				</div>
			</div>

			<div class="px-6 py-6">
				<!-- Organization Logos -->
				<div class="mb-6 flex items-center justify-center gap-3">
					{#if organization.dark_logo}
						<div class="bg-black dark:bg-gray-900 px-8 py-6 rounded-xl border border-gray-200 dark:border-gray-700">
							<img src={organization.dark_logo} alt="Dark Logo" class="h-20 w-auto object-contain" />
						</div>
					{/if}
					{#if organization.light_logo}
						<div class="bg-gray-100 dark:bg-gray-800 px-8 py-6 rounded-xl border border-gray-200 dark:border-gray-700">
							<img src={organization.light_logo} alt="Light Logo" class="h-20 w-auto object-contain" />
						</div>
					{/if}
					{#if !organization.dark_logo && !organization.light_logo}
						<div class="text-gray-400 dark:text-gray-500 text-sm py-8">
							{$i18n.t('No logos uploaded')}
						</div>
					{/if}
				</div>

				<!-- Organization Info -->
				<div class="space-y-3 mb-6">
					<!-- Name -->
					<div class="bg-blue-50/70 dark:bg-blue-900/10 rounded-xl p-4 border border-blue-100 dark:border-blue-900/30">
						<div class="text-xs font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wide mb-1.5">
							{$i18n.t('Name')}
						</div>
						<div class="text-lg font-bold text-gray-900 dark:text-gray-100">
							{organization.org_name || 'N/A'}
						</div>
					</div>

					<!-- Code -->
					<div class="bg-blue-50/70 dark:bg-blue-900/10 rounded-xl p-4 border border-blue-100 dark:border-blue-900/30">
						<div class="text-xs font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wide mb-1.5">
							{$i18n.t('Code')}
						</div>
						<div class="text-lg font-mono font-bold text-gray-900 dark:text-gray-100">
							{organization.org_code || 'N/A'}
						</div>
					</div>

					<!-- Plans -->
					<div class="bg-blue-50/70 dark:bg-blue-900/10 rounded-xl p-4 border border-blue-100 dark:border-blue-900/30">
						<div class="text-xs font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wide mb-2.5">
							{$i18n.t('Plans')}
						</div>
						<div class="space-y-2">
							{#if organization.plans && organization.plans.length > 0}
								{#each organization.plans as planId}
									<div class="flex items-start gap-2.5">
										<div class="w-1.5 h-1.5 bg-blue-600 dark:text-blue-400 rounded-full mt-1.5 flex-shrink-0"></div>
										<span class="text-base font-semibold text-gray-900 dark:text-gray-100 leading-tight">
											{getPlanName(planId)}
										</span>
									</div>
								{/each}
							{:else}
								<div class="text-sm text-gray-500 dark:text-gray-400 italic">
									{$i18n.t('No plans assigned')}
								</div>
							{/if}
						</div>
					</div>
				</div>

				<!-- Registration Link -->
				<div class="bg-white dark:bg-gray-800/50 rounded-xl p-4 border border-gray-300 dark:border-gray-700">
					<div class="flex items-center justify-between gap-2 mb-2.5">
						<div class="text-xs font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wide">
							{$i18n.t('Registration Link')}
						</div>
						<button
							class="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition text-gray-600 dark:text-gray-400"
							on:click={copySignupLink}
							title={$i18n.t('Copy')}
						>
							<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
								<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
							</svg>
						</button>
					</div>
					<div class="text-sm font-mono text-gray-700 dark:text-gray-300 break-all bg-gray-50 dark:bg-gray-900/30 px-3 py-2 rounded-lg">
						{signupUrl}
					</div>
				</div>
			</div>
		</div>
	</Modal>
{/if}

<ConfirmDialog
	bind:show={showDeleteConfirm}
	title={$i18n.t('Confirm Deletion')}
	confirmLabel={$i18n.t('Delete')}
	onConfirm={onDelete}
>
	<div class="text-sm text-gray-500 dark:text-gray-400">
		{$i18n.t('Are you sure you want to delete the organization')}
		<span class="font-bold text-gray-900 dark:text-gray-100">{organization.org_name}</span>?
		<br /><br />
		{$i18n.t('This action cannot be undone.')}
	</div>
</ConfirmDialog>
