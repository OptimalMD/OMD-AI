<script>
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';
	import relativeTime from 'dayjs/plugin/relativeTime';
	dayjs.extend(relativeTime);

	import { onMount, getContext } from 'svelte';
	import { goto } from '$app/navigation';

	import { config, user } from '$lib/stores';

	import Tooltip from '$lib/components/common/Tooltip.svelte';
	import Plus from '$lib/components/icons/Plus.svelte';
	import Search from '$lib/components/icons/Search.svelte';
	import CreditCard from '$lib/components/icons/CreditCard.svelte';
	import Pencil from '$lib/components/icons/Pencil.svelte';
	import GarbageBin from '$lib/components/icons/GarbageBin.svelte';
	import EditPlanModal from './Plans/EditPlanModal.svelte';
	import ConfirmDialog from '$lib/components/common/ConfirmDialog.svelte';

	import {
		getSubscriptionPlans,
		createPlan,
		updatePlan,
		deletePlan
	} from '$lib/apis/subscriptions';
	import { getModels } from '$lib/apis';

	const i18n = getContext('i18n');

	let loaded = false;
	let plans = [];
	let filteredPlans;
	let models = [];

	// Function to get model name from ID
	const getModelName = (modelId) => {
		const model = models.find(m => m.id === modelId);
		return model?.name || model?.id || modelId;
	};

	$: filteredPlans = plans.filter((plan) => {
		if (search === '') {
			return true;
		} else {
			let name = plan.plan_name.toLowerCase();
			const query = search.toLowerCase();
			return name.includes(query);
		}
	});

	let search = '';
	let showAddPlanModal = false;
	let showEditPlanModal = false;
	let selectedPlan = null;
	let showDeleteConfirm = false;
	let planToDelete = null;

	const setPlans = async () => {
		try {
			const res = await getSubscriptionPlans(localStorage.token);
			if (res) {
				plans = res.map(plan => ({
					...plan,
					// Map backend fields to frontend fields
					active: plan.is_active
				}));
			}
		} catch (error) {
			toast.error(`${error}`);
			console.error('Error fetching plans:', error);
		}
	};

	const loadModels = async () => {
		try {
			const res = await getModels(localStorage.token);
			if (res) {
				models = res.data || res || [];
			}
		} catch (error) {
			console.error('Error loading models:', error);
		}
	};

	const addPlanHandler = async (planData) => {
		try {
			console.log('Creating plan with data:', planData);
			console.log('Models selected:', planData.models);
			const res = await createPlan(localStorage.token, planData);
			if (res) {
				console.log('Plan created:', res);
				toast.success($i18n.t('Plan created successfully'));
				await setPlans();
			}
		} catch (error) {
			toast.error(`${error}`);
			console.error('Error creating plan:', error);
		}
	};

	const updatePlanHandler = async (planData) => {
		if (!selectedPlan) return;
		
		try {
			const res = await updatePlan(localStorage.token, selectedPlan.id, planData);
			if (res) {
				toast.success($i18n.t('Plan updated successfully'));
				await setPlans();
				selectedPlan = null;
			}
		} catch (error) {
			toast.error(`${error}`);
			console.error('Error updating plan:', error);
		}
	};

	const deletePlanHandler = async (planId) => {
		planToDelete = planId;
		showDeleteConfirm = true;
	};

	const confirmDelete = async () => {
		if (!planToDelete) return;

		try {
			const res = await deletePlan(localStorage.token, planToDelete);
			if (res) {
				toast.success($i18n.t('Plan deleted successfully'));
				await setPlans();
			}
		} catch (error) {
			toast.error(`${error}`);
			console.error('Error deleting plan:', error);
		} finally {
			planToDelete = null;
		}
	};

	const editPlanHandler = (plan) => {
		selectedPlan = plan;
		showEditPlanModal = true;
	};

	onMount(async () => {
		if ($user?.role !== 'admin') {
			await goto('/');
			return;
		}

		await loadModels();
		await setPlans();
		loaded = true;
	});
</script>

{#if loaded}
	<!-- Add Plan Modal -->
	<EditPlanModal
		bind:show={showAddPlanModal}
		edit={false}
		onSubmit={addPlanHandler}
	/>

	<!-- Edit Plan Modal -->
	<EditPlanModal
		bind:show={showEditPlanModal}
		edit={true}
		plan={selectedPlan}
		onSubmit={updatePlanHandler}
	/>

	<!-- Delete Confirmation Dialog -->
	<ConfirmDialog
		bind:show={showDeleteConfirm}
		title={$i18n.t('Confirm Deletion')}
		message={$i18n.t('Are you sure you want to delete this plan? This action cannot be undone.')}
		confirmLabel={$i18n.t('Delete')}
		cancelLabel={$i18n.t('Cancel')}
		onConfirm={confirmDelete}
	/>

	<div class="mt-0.5 mb-6 gap-1 flex flex-col md:flex-row justify-between items-center">
		<div class="flex md:self-center text-2xl font-bold px-0.5 text-gray-800 dark:text-gray-100">
			{$i18n.t('Subscription Plans')}
		</div>

		<div class="flex gap-2">
			<div class=" flex w-full space-x-2">
				<div class="flex flex-1 relative">
					<div class="absolute left-0 top-0 bottom-0 flex items-center pl-3 pointer-events-none text-gray-500">
						<Search className="size-4" />
					</div>
					<input
						class="w-full text-sm pl-9 pr-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 outline-none focus:ring-2 focus:ring-blue-500"
						bind:value={search}
						placeholder={$i18n.t('Search Plans')}
					/>
				</div>

				<div>
					<button
						class="px-4 py-2 rounded-lg bg-green-500 hover:bg-green-600 text-white transition font-medium text-sm flex items-center space-x-1 shadow-sm"
						on:click={() => {
							showAddPlanModal = true;
						}}
					>
						<Plus className="size-3.5" />
						<span>{$i18n.t('Add Plan')}</span>
					</button>
				</div>
			</div>
		</div>
	</div>

	<div>
		{#if filteredPlans.length === 0}
			<div class="flex flex-col items-center justify-center h-40">
				<div class=" text-xl font-medium">
					{$i18n.t('Manage subscription plans')}
				</div>

				<div class="mt-1 text-sm dark:text-gray-300">
					{$i18n.t('Create and manage subscription plans for your users.')}
				</div>

				<div class="mt-3">
					<button
						class=" px-4 py-1.5 text-sm rounded-full bg-green-500 hover:bg-green-600 text-white transition font-medium flex items-center space-x-1"
						aria-label={$i18n.t('Create Plan')}
						on:click={() => {
							showAddPlanModal = true;
						}}
					>
						{$i18n.t('Create Plan')}
					</button>
				</div>
			</div>
		{:else}
			<div class="grid grid-cols-1 md:grid-cols-2 gap-6">
				{#each filteredPlans as plan}
					<div class="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-800 shadow-sm flex flex-col h-full relative hover:shadow-md transition-shadow">
						<!-- Header -->
						<div class="text-center mb-6 bg-gray-50 dark:bg-gray-800 p-4 rounded-lg">
							<h3 class="text-xl font-bold text-gray-900 dark:text-gray-100 mb-3">{plan.plan_name}</h3>
							
							<div class="flex justify-center mb-4">
								<span class="bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300 px-5 py-1.5 rounded-full text-lg font-bold">
									{#if plan.price === 0}
										{$i18n.t('Free')}
									{:else}
										${plan.price} <span class="text-sm font-normal text-blue-500 dark:text-blue-400">per {plan.duration_type || 'month'}</span>
									{/if}
								</span>
							</div>
							
							{#if plan.subtitle}
								<p class="text-gray-500 dark:text-gray-400 text-sm">{plan.subtitle}</p>
							{/if}
						</div>

						<!-- Models -->
						{#if plan.models && plan.models.length > 0}
							<div class="mb-6 px-4">
								<p class="text-xs font-bold text-gray-400 uppercase mb-2">{$i18n.t('Available Models')}:</p>
								<div class="flex flex-wrap gap-2">
									{#each plan.models as model}
										<span class="bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-300 px-2.5 py-1 rounded text-xs font-medium border border-blue-100 dark:border-blue-800">
											{getModelName(model)}
										</span>
									{/each}
								</div>
							</div>
						{/if}

						<!-- Features -->
						<div class="flex-grow mb-6 px-4">
							{#if plan.benefits && plan.benefits.length > 0}
								<ul class="space-y-2.5">
									{#each plan.benefits as benefit}
										<li class="flex items-start gap-2.5 text-sm text-gray-600 dark:text-gray-300">
											<span class="text-green-500 mt-0.5 shrink-0">
												<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" class="w-4 h-4">
													<path fill-rule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clip-rule="evenodd" />
												</svg>
											</span>
											<span class="leading-tight">{benefit}</span>
										</li>
									{/each}
								</ul>
							{/if}
						</div>

						<!-- Additional Info -->
						{#if plan.additional_info}
							<div class="mb-6 pt-4 border-t border-gray-100 dark:border-gray-800 px-4">
								<p class="text-[10px] italic text-gray-500 dark:text-gray-400 leading-relaxed">
									{plan.additional_info}
								</p>
							</div>
						{/if}

						<!-- Footer Actions -->
						<div class="flex justify-end gap-3 p-4 mt-auto">
							<button
								class="flex items-center gap-1.5 px-3 py-1.5 text-blue-600 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:text-blue-300 dark:hover:bg-blue-900/40 rounded-lg transition text-sm font-medium"
								on:click={() => editPlanHandler(plan)}
							>
								<Pencil className="size-3.5" />
								{$i18n.t('Edit')}
							</button>

							<button
								class="flex items-center gap-1.5 px-3 py-1.5 text-red-600 bg-red-50 hover:bg-red-100 dark:bg-red-900/20 dark:text-red-300 dark:hover:bg-red-900/40 rounded-lg transition text-sm font-medium"
								on:click={() => deletePlanHandler(plan.id)}
							>
								<GarbageBin className="size-3.5" />
								{$i18n.t('Delete')}
							</button>
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
{/if}
