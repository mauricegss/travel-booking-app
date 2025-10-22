interface DestinationCardProps {
  image: string;
  title: string;
  description: string;
  price: string;
}

export const DestinationCard = ({ image, title, description, price }: DestinationCardProps) => {
  return (
    <div className="group relative overflow-hidden rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer">
      <div className="aspect-[4/3] overflow-hidden">
        <img 
          src={image} 
          alt={title}
          className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
        />
      </div>
      <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
        <h3 className="text-2xl font-bold mb-2">{title}</h3>
        <p className="text-sm text-white/90 mb-3">{description}</p>
        <div className="flex items-center justify-between">
          <span className="text-lg font-semibold">A partir de {price}</span>
        </div>
      </div>
    </div>
  );
};
