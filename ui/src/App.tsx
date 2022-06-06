import React from 'react';
import { Layout, Breadcrumb } from 'antd';
import {
  FileOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import './App.css';
import { Routes, Route } from "react-router-dom";
import GallerySubmit from './components/GallerySubmit'
import HeaderMenu from './components/HeaderMenu'
import ImageSpaceControls from './components/ImageSpaceControls'

import PixivArtistView from './components/pixiv/PixivArtistView';
import PixivGalleryView from './components/pixiv/PixivGalleryView';
import PixivImagesView from './components/pixiv/PixivImagesView';

import DaArtistView from './components/da/DaArtistView';
import DaGalleryView from './components/da/DaGalleryView';
import DaImagesView from './components/da/DaImagesView';



const { Header, Content, Footer } = Layout;


type MenuItem = Required<MenuProps>['items'][number];

function getItem(
  label: React.ReactNode,
  key: React.Key,
  icon?: React.ReactNode,
  children?: MenuItem[],
): MenuItem {
  return {
    key,
    icon,
    children,
    label,
  } as MenuItem;
}

var URL: string;

if (typeof window !== 'undefined') {
  URL = window.location.protocol + '//' + window.location.host;
} else {
  URL = "http://0.0.0.0/"
}

const items: MenuItem[] = [
  getItem('URL Gallery Downloader', '1', <FileOutlined />),
];

const App: React.FC = () => {
  return (
    <Layout>
      <Header style={{ position: 'fixed', padding: 0, zIndex: 1, width: '100%' }}>
        <HeaderMenu />
      </Header>
      <Content className="site-layout" style={{ padding: '0 50px', marginTop: 64 }}>
        <div className="site-layout-background" style={{ padding: 24, minHeight: 800 }}>
          <Routes>
            <Route path="/">
              <Route index element={<GallerySubmit apiUrl={URL} />} />
              <Route path="grid">
                <Route path="pixiv" >
                  <Route path="artist/:artistid" element={<PixivGalleryView apiUrl={URL} />} />
                  <Route path="gallery/:galleryid" element={<PixivImagesView apiUrl={URL} />} />
                  <Route index element={<PixivArtistView apiUrl={URL} />} />
                </Route>
                <Route path="da" >
                  <Route path="artist/:artistid" element={<DaGalleryView apiUrl={URL} />} />
                  <Route path="gallery/:galleryid" element={<DaImagesView apiUrl={URL} />} />
                  <Route index element={<DaArtistView apiUrl={URL} />} />
                </Route>
              </Route>
              <Route path="settings">
                <Route index element={<ImageSpaceControls />} />
              </Route>
            </Route>
          </Routes>
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>yeah</Footer>
    </Layout>
  );
}





// {
//   const [collapsed, setCollapsed] = useState(false);

//   return (
//     <Layout style={{ minHeight: '100vh' }}>
//       <Sider collapsible collapsed={collapsed} onCollapse={value => setCollapsed(value)}>
//         <div className="logo" />
//         <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline" items={items} />
//       </Sider>
//       <Layout className="site-layout">
//         <Header className="site-layout-background" style={{ padding: 0 }} />
//         <Content style={{ margin: '0 16px' }}>
//         </Content>
//         <Footer style={{ textAlign: 'center' }}></Footer>
//       </Layout>
//     </Layout>
//   );
// };

export default App;