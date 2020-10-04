CREATE DATABASE IF NOT EXISTS `recruit`;
USE `recruit`;

CREATE TABLE IF NOT EXISTS `doda` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `company_name` varchar(100) NOT NULL,
  `url_doda` varchar(255) NOT NULL,
  `postal_code` varchar(8) NULL,
  `address` varchar(255) NULL,
  `TEL` varchar(11) NULL,
  `remarks` varchar(255) NULL,
  `url_company` varchar(255) NULL,
  PRIMARY KEY (`id`)
);

insert into doda (company_name, url_doda, postal_code, address) \
    values ('株式会社AAAAAA', 'https://www.yahoo.co.jp/', '000-0000', '東京都港区赤坂0-0-0 赤坂ビル0F');
insert into doda (company_name, url_doda, postal_code, address) \
    values ('株式会社BBBBBB', 'https://www.yahoo.co.jp/', '000-0000', '東京都港区赤坂0-0-0 赤坂ビル0F');
insert into doda (company_name, url_doda, postal_code, address) \
    values ('株式会社CCCCCC', 'https://www.yahoo.co.jp/', '000-0000', '東京都港区赤坂0-0-0 赤坂ビル0F');
insert into doda (company_name, url_doda, postal_code, address) \
    values ('株式会社DDDDDD', 'https://www.yahoo.co.jp/', '000-0000', '東京都港区赤坂0-0-0 赤坂ビル0F');
insert into doda (company_name, url_doda, postal_code, address) \
    values ('株式会社EEEEEE', 'https://www.yahoo.co.jp/', '000-0000', '東京都港区赤坂0-0-0 赤坂ビル0F');