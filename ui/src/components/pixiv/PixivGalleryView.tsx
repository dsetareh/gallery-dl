import { useEffect, useState, useRef } from 'react';
import { Space, Image, Card, Badge, Row, Col, Button, notification, Pagination, Divider } from 'antd';
import Cookies from 'universal-cookie';
import { CloudDownloadOutlined, LinkOutlined } from '@ant-design/icons';
import { useParams } from "react-router-dom";

const { Meta } = Card;
interface IPixivGalleryViewProps {
    apiUrl: string
}

interface IGalleryGet {
    ID: number,
    GALLERY_NAME: string,
    NUM_IMAGES: number,
    GALLERY_VIEWS: number,
    DIRECTORYNAME: string,
    GALLERY_URL: string,
    CREATED_DATE: string,
    FILENAME: string,
    WIDTH: number,
    HEIGHT: number
}

const cookies = new Cookies();

const PixivGalleryView = (props: IPixivGalleryViewProps) => {
    const [galleryData, setGalleryData] = useState<IGalleryGet[]>([])
    const [imgSize, setImgSize] = useState<number>(200)
    let params = useParams();

    const loadGalleries = async () => {
        const response = await fetch(`${props.apiUrl}/api/pixiv/gallery/${params.artistid}`);
        const galleries = await response.json();
        setGalleryData(galleries)
    }

    useEffect(() => {

        loadGalleries()

        const cookImgSize = cookies.get("imgSize")
        if (typeof cookImgSize === "string") {
            const cookImgNumSize = Number(cookImgSize)
            if (cookImgNumSize >= 100 && cookImgNumSize <= 500)
                setImgSize(cookImgNumSize)

        }

    }, []);



    const generateGalleryCard = (gallData: IGalleryGet) => {
        return (
            <Card
                style={{ width: imgSize, height: imgSize + 100 }}
                cover={
                    generateCardImage(gallData)
                }
            >
                <a href={`${props.apiUrl}/grid/pixiv/gallery/${gallData.ID}`}>
                    <Meta style={{ position: "relative", bottom: 0, left: 0, margin: "10px" }}
                        title={`${gallData.GALLERY_NAME} ${gallData.GALLERY_VIEWS}`}
                        description={`${gallData.NUM_IMAGES} Image${gallData.NUM_IMAGES == 1 ? '' : 's'}`}
                    />
                </a>
            </Card>
        )
    }

    const generateCardImage = (gallData: IGalleryGet) => {
        const limiting_factor = Math.max(gallData.HEIGHT, gallData.WIDTH);
        const resize_scale = limiting_factor / imgSize;
        const resized_width = Math.floor(gallData.WIDTH / resize_scale)
        const resized_height = Math.floor(gallData.HEIGHT / resize_scale)
        const leftover_width = Math.floor((imgSize - resized_width) / 2)
        return (
            <div style={{ height: resized_height, width: resized_width, left: leftover_width, position: "relative" }}>
                <Image
                    src={`${props.apiUrl}/${gallData.DIRECTORYNAME}/${gallData.FILENAME}.webp`}
                />
            </div>


        )
    }


    return (
        <>
            <Row>
                <Col span={24}>
                    <Space size={[8, 16]} wrap>
                        {galleryData.map((galldata) => generateGalleryCard(galldata))}
                        {galleryData.length == 0 ? "Nothing Here...." : ""}
                    </Space>
                </Col>
            </Row>
        </>
    )


}


export default PixivGalleryView;