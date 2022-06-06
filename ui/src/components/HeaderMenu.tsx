import React from 'react';
import { Menu } from 'antd';
import { Link } from "react-router-dom";

import { PlusCircleOutlined, DatabaseOutlined, SettingOutlined } from '@ant-design/icons';

const HeaderMenu: React.FC = () => {
    return (
        <Menu mode="horizontal" defaultSelectedKeys={['mail']}>

            <Menu.Item key="add" icon={<PlusCircleOutlined />}>
                <Link to="/">
                    Add Gallery
                </Link>
            </Menu.Item>

            <Menu.Item key="grid" icon={<DatabaseOutlined />}>
                <Link to="/grid/pixiv">
                    Pixiv
                </Link>
            </Menu.Item>

            <Menu.Item key="grid" icon={<DatabaseOutlined />}>
                <Link to="/grid/da">
                    DA
                </Link>
            </Menu.Item>

            <Menu.Item key="settings" icon={<SettingOutlined />}>
                <Link to="/settings">
                    Settings
                </Link>
            </Menu.Item>

        </Menu>
    )
};

export default HeaderMenu;