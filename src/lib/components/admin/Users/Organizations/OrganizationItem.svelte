<script lang="ts">
	import { toast } from 'svelte-sonner';
	import { getContext } from 'svelte';

	const i18n = getContext('i18n');

	import Eye from '$lib/components/icons/Eye.svelte';
	import Pencil from '$lib/components/icons/Pencil.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';
	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	export let organization: any = {};
	export let plans: any[] = [];
	export let onView = () => {};
	export let onEdit = () => {};
	export let onDelete = () => {};
	export let onDuplicate = () => {};

	let showDeleteConfirm = false;

	$: plansList = organization.plans || [];
	$: userCount = organization.users ? organization.users.length : 0;
	
	const getPlanName = (planId: string) => {
		// Find the plan in the plans array
		const plan = plans.find((p: any) => p.id === planId);
		if (plan && plan.plan_name) {
			return plan.plan_name;
		}
		// Fallback to formatting the plan ID
		return formatPlanName(planId);
	};
	
	const getPlanBadgeColor = (planId: string) => {
		// Default colors for different plan types
		const colors = {
			'freemium': 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',
			'premium': 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
			'enterprise': 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400'
		};
		
		const lowerPlanId = planId.toLowerCase();
		if (lowerPlanId.includes('freemium') || lowerPlanId.includes('free')) {
			return colors.freemium;
		} else if (lowerPlanId.includes('premium') || lowerPlanId.includes('pro')) {
			return colors.premium;
		} else if (lowerPlanId.includes('enterprise')) {
			return colors.enterprise;
		}
		return colors.premium;
	};
	
	const formatPlanName = (planId: string) => {
		// Format plan ID to display name
		// Convert snake_case, kebab-case, or camelCase to Title Case
		return planId
			.replace(/([A-Z])/g, ' $1') // Add space before capital letters
			.replace(/[_-]/g, ' ') // Replace underscores and hyphens with spaces
			.trim()
			.split(' ')
			.map((word: string) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
			.join(' ');
	};
</script>

<tr class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
	<!-- Name Column -->
	<td class="px-6 py-4">
		<div class="flex flex-col">
			<div class="text-sm font-medium text-gray-900 dark:text-gray-100">
				{organization.org_name}
			</div>
			{#if userCount > 0}
				<div class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
					({userCount})
				</div>
			{/if}
		</div>
	</td>

	<!-- Code Column -->
	<td class="px-6 py-4">
		<div class="text-sm font-mono text-gray-700 dark:text-gray-300">
			{organization.org_code}
		</div>
	</td>

	<!-- Plans Column -->
	<td class="px-6 py-4">
		<div class="flex flex-wrap gap-1.5">
			{#if plansList.length > 0}
				{#each plansList as planId}
					<span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium {getPlanBadgeColor(planId)}">
						{getPlanName(planId)}
					</span>
				{/each}
			{:else}
				<span class="text-sm text-gray-400 dark:text-gray-500">
					{$i18n.t('No plans')}
				</span>
			{/if}
		</div>
	</td>

	<!-- Actions Column -->
	<td class="px-6 py-4">
		<div class="flex items-center justify-end gap-1">
			<Tooltip content={$i18n.t('View Details')}>
				<button
					class="p-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 text-blue-600 dark:text-blue-400 transition"
					on:click={onView}
					aria-label={$i18n.t('View')}
				>
					<Eye className="size-4" />
				</button>
			</Tooltip>

			<Tooltip content={$i18n.t('Edit')}>
				<button
					class="p-2 rounded-lg hover:bg-purple-50 dark:hover:bg-purple-900/20 text-purple-600 dark:text-purple-400 transition"
					on:click={onEdit}
					aria-label={$i18n.t('Edit')}
				>
					<Pencil className="size-4" />
				</button>
			</Tooltip>

			<Tooltip content={$i18n.t('Delete')}>
				<button
					class="p-2 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20 text-red-600 dark:text-red-400 transition"
					on:click={() => {
						showDeleteConfirm = true;
					}}
					aria-label={$i18n.t('Delete')}
				>
					<GarbageBin className="size-4" />
				</button>
			</Tooltip>

			<Tooltip content={$i18n.t('Copy Signup Link')}>
				<button
					class="p-2 rounded-lg hover:bg-green-50 dark:hover:bg-green-900/20 text-green-600 dark:text-green-400 transition"
					on:click={onDuplicate}
					aria-label={$i18n.t('Copy Signup Link')}
				>
					<svg class="size-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
					</svg>
				</button>
			</Tooltip>
		</div>
	</td>
</tr>

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
