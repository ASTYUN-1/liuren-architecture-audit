"""Verified same-event additions; never copy the neighbour's question/feedback."""
def add(CASES,ref):
    p='书籍库/现代著作/《壬占汇选》.txt'
    rows=[
      (36,339,6339,6351,'刘经历代梁司马推冢宰、日马坐墓及请告退位同案；古三月与毕法四月并留。古6351末句万公壬申辰时是另占，不用作梁案输入。'),
      (40,323,6041,6057,'甲申五月乙未未时、张四知费县、屯兵与渡江同案；古6041明确申将补将，原盘酉玄戌阴亥后可核。蒿矢/昴星原说并存，不把课名差异洗平。'),
      (79,371,6931,6933,'只对应刘汉式复旧缺的愚按子问与过程后析；古6929眷属行人问为同课另一题，不能拿其反馈补本题。'),
      (81,366,6825,6841,'癸未正月己亥未时、金陵索占的赵忻城昆弟及六月钦召同事件；古明确亥将可用于另存补证请求，不把授职历史独立认证。'),
      (83,293,5497,5513,'壬辰酉将寅时杀二人问赦/处决同案；不得与另两人合打一人案合并。'),
      (84,410,7631,7645,'甲辰戌将寅失狗、戌临日与末寅虎克及木排人杀同案；毕法白狗/古未载色、杀/杀烹差别保留。'),
      (85,387,7205,7221,'戊申九月壬寅辰将酉、邵梓材、九年宅改田、戊午亡及己未蚁坟同案；亡祟、坟与疾病因果只原说。'),
    ]
    for n,k,a,b,note in rows:
        c=next(c for c in CASES if c['id']==f'BK26-BIFA-{n:03}')
        ident=f'BK26-ANCIENT-{k:03}'
        if ident not in c['same_event_ids']:c['same_event_ids'].append(ident)
        c['source_refs'].append({**ref(p,a,b),'dependency_type':'same_event_parallel_source','same_event':True})
        c['notes'].append('跨书逐段对读补证：'+note+' 同事件重引不增加独立样本或验证。')
