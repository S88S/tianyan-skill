# SSL 三层结构规范（天演自研表述）

SSL（Scheduling–Structural–Logical）把一份技能产物表达为**三层相互链接的 JSON 图**。
天演按此结构描述自身，并在 Phase 3「程序门」用 `scripts/validate_ssl_record.py` 校验记录。

> 说明：字段名与受控取值是 SSL 的接口契约，为兼容既有记录而沿用；
> 本文的表述、组织与举例为天演独立编写。

---

## 一、三层各司何职

| 层 | 粒度 | 回答的问题 |
|---|---|---|
| **调度层 Scheduling** | 技能 | 这个技能是干什么的、何时被调用（对外能力表面） |
| **结构层 Structural** | 场景 scene | 执行被切成哪几段、每段的目标与出入口是什么 |
| **逻辑层 Logical** | 步骤 logic step | 每段里具体做了哪些原子动作、用了什么资源 |

**跨层只保留两类关系**：包含（场景属于技能、步骤属于场景）与入口指针（从声明的入口开始遍历）。
这样，接口信息、阶段结构、动作与资源证据各安其位，互不掺杂。

---

## 二、调度层字段

技能级记录，供能力匹配与触发判断：

`skill_id` · `skill_name` · `skill_goal` · `intent_signature` · `tags` · `top_pattern` ·
`expected_inputs` · `expected_outputs` · `dependencies` · `control_flow_features` ·
`entry_scene_id` · `subscenes`

该层只承载稳定的对外表面，不重复整张执行图。

---

## 三、结构层字段

场景级记录：

`scene_id` · `scene_name` · `scene_type` · `scene_goal` · `input` · `output` ·
`entry_conditions` · `exit_conditions` · `next_scene_rules` ·
`entry_logic_step_id` · `contained_logic_steps`

一个场景对应一段**内聚的执行阶段**，有自己的目标、数据契约与退出条件；
场景之间的跳转由 `next_scene_rules` 描述。

---

## 四、逻辑层字段

步骤级记录：

`logic_step_id` · `act_type` · `actor` · `object` · `instrument` · `input_args` ·
`output_binding` · `preconditions` · `effects` ·
`resource_scope` · `resource_target` · `next_step_rules`

逻辑步骤是**源产物能支撑的最小操作单元**，不得杜撰源中没有的实现细节。
当动作类型、资源边界、效果或控制流结果发生变化时，应拆分为新的步骤。

---

## 五、受控取值

**scene_type**：`PREPARE`、`ACQUIRE`、`REASON`、`ACT`、`VERIFY`、`RECOVER`、`FINALIZE`

**act_type**：`READ`、`SELECT`、`COMPARE`、`VALIDATE`、`INFER`、`WRITE`、
`UPDATE_STATE`、`CALL_TOOL`、`REQUEST`、`TRANSFER`、`NOTIFY`、`TERMINATE`

**resource_scope**：`MEMORY`、`LOCAL_FS`、`CODEBASE`、`PROCESS`、
`USER_DATA`、`CREDENTIALS`、`NETWORK`、`OTHER`

**保留终态**：场景层 `END_SUCCESS` / `END_FAIL`；步骤层 `YIELD_SUCCESS` / `YIELD_FAIL`
