-- 创建积分兑换现实货币汇率表
CREATE TABLE IF NOT EXISTS `tb_points_exchange_rate` (
  `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `currency_code` VARCHAR(10) NOT NULL COMMENT '货币代码（如：CNY、USD、EUR）',
  `currency_name` VARCHAR(50) NOT NULL COMMENT '货币名称（如：人民币、美元、欧元）',
  `exchange_rate` DECIMAL(10,4) NOT NULL COMMENT '兑换汇率（1积分=X货币）',
  `symbol` VARCHAR(10) NOT NULL COMMENT '货币符号（如：¥、$、€）',
  `is_active` BOOLEAN DEFAULT TRUE COMMENT '是否启用',
  `rdatetime` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `udatetime` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_currency_code` (`currency_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='积分兑换现实货币汇率表';

-- 插入默认数据
INSERT INTO `tb_points_exchange_rate` (`currency_code`, `currency_name`, `exchange_rate`, `symbol`, `is_active`) VALUES
('CNY', '人民币', 0.0100, '¥', 1),
('USD', '美元', 0.0014, '$', 1),
('EUR', '欧元', 0.0013, '€', 1);