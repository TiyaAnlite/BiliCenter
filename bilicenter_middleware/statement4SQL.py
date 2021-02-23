def make_update_query(table: str, data_struct: dict, keys_struct: dict = None) -> tuple:
    """
    辅助构造参数型UPDATE SQL语句帮助方法\n
    :param table: 表名
    :param data_struct: 参与构造的关键字结构
    :param keys_struct: (可选)条件关键字结构
    :return: 构造后的(query, args)
    """
    query = f"UPDATE `{table}` SET {','.join(f'`{k}`' + '=%s' for k in data_struct.keys())}"
    args = list(data_struct.values())
    if keys_struct:
        query += f" WHERE {' AND '.join(f'`{k}`' + '=%s' for k in keys_struct.keys())}"
        args.extend(keys_struct.values())
    return query, args


def make_insert_query(table: str, data_struct: dict, safety_mode=False, update=False) -> tuple:
    """
    辅助构造参数型INSERT SQL语句帮助方法\n
    :param table: 表名
    :param data_struct: 参与构造的关键字结构
    :param safety_mode: 安全模式：冲突时不插入
    :param update: 配合安全模式使用，冲突时自动转为Update
    :return: 构造后的(query, args)
    """
    if safety_mode and not update:
        query = "INSERT IGNORE INTO "
    else:
        query = "INSERT INTO "
    query += f"`{table}` ({','.join(f'`{k}`' for k in data_struct.keys())}) VALUES ({','.join('%s' for null in data_struct)})"
    args = list(data_struct.values())
    if safety_mode and update:
        query += f"ON DUPLICATE KEY UPDATE {','.join(f'`{k}`' + '=%s' for k in data_struct.keys())}"
        args.extend(data_struct.values())
    return query, args
