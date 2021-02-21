def make_update_query(table: str, data_struct: dict, keys_struct: dict = None) -> tuple:
    """
    辅助构造参数型UPDATE SQL语句帮助方法\n
    :param table: 表名
    :param data_struct: 参与构造的关键字结构
    :param keys_struct: (可选)条件关键字结构
    :return: 构造后的(query, args)
    """
    query = f"UPDATE `{table}` SET {','.join(f'`{n}`' + '=%s' for n in data_struct.keys())}"
    args = list(data_struct.values())
    if keys_struct:
        query += f" WHERE {' AND '.join(f'`{n}`' + '=%s' for n in keys_struct.keys())}"
        args.extend(keys_struct.values())
    return query, args
